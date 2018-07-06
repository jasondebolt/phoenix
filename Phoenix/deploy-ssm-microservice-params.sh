#!/bin/bash
set -e

# Creates SSM parameters for a microservice.
#
# USAGE
#   ./deploy-ssm-params.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Extract JSON properties for a file into a local variable
CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' ssm-microservice-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' ssm-microservice-params.json)
STACK_NAME=$PROJECT_NAME-ssm-microservice-params

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py ssm-microservice-params.json cloudformation > temp1.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://ssm-microservice.json

aws cloudformation $1-stack \
    --stack-name $STACK_NAME \
    --template-body file://ssm-microservice.json \
    --parameters file://temp1.json \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

if [[ $1 == 'create' ]]; then
  aws cloudformation update-termination-protection --enable-termination-protection --stack-name $STACK_NAME
fi

# Cleanup
rm temp1.json
