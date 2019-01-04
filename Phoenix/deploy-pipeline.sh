#!/bin/bash
set -e

# Creates the main AWS Code Pipeline for the microservice project.
#
# USAGE
#   ./deploy-pipeline.sh [create | update]

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
MICROSERVICE_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-microservice
STACK_NAME=$PROJECT_NAME-pipeline
ENVIRONMENT='all'
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" template-pipeline.json > temp0.json

aws s3 sync . s3://$MICROSERVICE_BUCKET_NAME/cloudformation --exclude "*" --include "template-*.json" --delete
aws s3 cp temp0.json s3://$MICROSERVICE_BUCKET_NAME/cloudformation/template-pipeline.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-pipeline.json

aws cloudformation create-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME \
    --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-pipeline.json \
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
