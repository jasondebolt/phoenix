#!/bin/bash
set -e

# Creates a Lambda CloudFormation Macro to post-process CloudFormation templates.
#
# USAGE
#   ./deploy-ssm-globals-macro.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Extract JSON properties for a file into a local variable
CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
LAMBDA_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-lambda
STACK_NAME=$PROJECT_NAME-ssm-globals-macro
ENVIRONMENT='all'
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`

# Upload the Python Lambda functions
listOfPythonLambdaFunctions='macro ssm_secret delete_network_interface'
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

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" template-ssm-globals-macro-params.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json cloudformation > temp2.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-ssm-globals-macro-params.json cloudformation > temp1.json

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" template-ssm-globals-macro.json > temp0.json
# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://temp0.json

aws cloudformation $1-stack \
    --stack-name $STACK_NAME \
    --template-body file://temp0.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

if [[ $1 == 'create' ]]; then
  aws cloudformation update-termination-protection --enable-termination-protection --stack-name $STACK_NAME
fi

# Cleanup
rm temp1.json
rm temp2.json
