#!/bin/bash
set -e

# Deploys a pull request API Gateway endpoint and Lambda handler to dynamically generate pull request pipelines.

# USAGE:
#   ./deploy-github-webhook-pull-request.sh [create | update]
#
# EXAMPLES:
#   ./deploy-github-webhook-pull-request.sh create
#   ./deploy-github-webhook-pull-request.sh update

# Extract JSON properties for a file into a local variable
CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
MICROSERVICE_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-microservice
LAMBDA_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-lambda
ENVIRONMENT='all'
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
STACK_NAME=$PROJECT_NAME-pull-request-webhook
CHANGE_SET_NAME=$VERSION_ID
# Allow developers to name the environment whatever they want, supporting multiple dev environments.

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Convert create/update to uppercase
OP=$(echo $1 | tr '/a-z/' '/A-Z/')

aws s3 sync . s3://$MICROSERVICE_BUCKET_NAME/cloudformation --exclude "*" --include "template-pull-request-pipeline.json" --delete

# Upload the Lambda functions
listOfLambdaFunctions='pull_request_webhook create_pull_request_webhook post_pullrequests'
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

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-github-webhook-pull-request-params.json cloudformation > temp1.json

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" temp1.json > temp2.json

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" template-github-webhook.json > temp0.json
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

if [[ $1 == 'create' ]]; then
  aws cloudformation update-termination-protection --enable-termination-protection --stack-name $STACK_NAME
fi

# Cleanup
rm temp1.json
rm temp2.json
