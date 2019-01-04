#!/bin/bash
set -e

# Deploys the 'API Internals' CloudFormation stack for fine-grained API tuning.
# This is API configuration that is too verbose to fit into CloudFormation templates.

# USAGE:
#   ./deploy-dev-api-deployment.sh [create | update]
#
# EXAMPLES:
#   ./deploy-dev-api-deployment.sh create
#   ./deploy-dev-api-deployment.sh update

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
ENVIRONMENT=`jq -r '.Parameters.Environment' template-api-params-dev.json`
STACK_NAME=$PROJECT_NAME-api-deployment-$ENVIRONMENT
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

listOfLambdaFunctions='api_internals'
for functionName in $listOfLambdaFunctions
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

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" template-api-deployment-params-dev.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json cloudformation > temp2.json

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" template-api-deployment.json > temp0.json
# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://temp0.json

aws cloudformation create-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME \
    --template-body file://temp0.json \
    --parameters file://temp2.json \
    --change-set-type $OP \
    --capabilities CAPABILITY_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait change-set-create-complete \
    --change-set-name $CHANGE_SET_NAME --stack-name $STACK_NAME

# Let's automatically execute the change-set for now
aws cloudformation execute-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME
