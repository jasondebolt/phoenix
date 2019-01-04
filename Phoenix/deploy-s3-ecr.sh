#!/bin/bash
set -e

# Creates S3 buckets and ECR repositories for a microservice.
#
# USAGE
#   ./deploy-s3-ecr.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Convert create/update to uppercase
OP=$(echo $1 | tr '/a-z/' '/A-Z/')

if [ -d "builds" ]; then
  echo deleting builds dir
  rm -rf builds
fi

# Extract JSON properties for a file into a local variable
CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
LAMBDA_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-lambda
STACK_NAME=$PROJECT_NAME-s3-ecr
ENVIRONMENT='all'
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

# Generate the lambda bucket if it doesn't already exist
# We have to create this bucket outside of the s3 bucket stack since
# the s3 stack launches a lambda function that depends on the source code
# within this bucket already existing.
aws s3 mb s3://$LAMBDA_BUCKET_NAME || true

# Upload the Python Lambda functions
listOfPythonLambdaFunctions='delete_s3_files delete_ecr_repos'
for functionName in $listOfPythonLambdaFunctions
do
  mkdir -p builds/$functionName
  cp -rf lambda/$functionName/* builds/$functionName/
  cd builds/$functionName/
  pip install -r requirements.txt -t .
  zip -r lambda_function.zip ./*
  aws s3 cp lambda_function.zip s3://$LAMBDA_BUCKET_NAME/$VERSION_ID/$functionName/
  cd ../../
  rm -rf builds
done

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-s3-ecr.json

aws cloudformation create-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME \
    --template-body file://template-s3-ecr.json \
    --parameters \
        ParameterKey=OrganizationName,ParameterValue=$ORGANIZATION_NAME \
        ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        ParameterKey=IAMRole,ParameterValue=$CLOUDFORMATION_ROLE \
        ParameterKey=Version,ParameterValue=$VERSION_ID \
    --change-set-type $OP \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait change-set-create-complete \
    --change-set-name $CHANGE_SET_NAME --stack-name $STACK_NAME

# Let's automatically execute the change-set for now
aws cloudformation execute-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

if [[ $1 == 'create' ]]; then
  aws cloudformation update-termination-protection --enable-termination-protection --stack-name $STACK_NAME
fi
