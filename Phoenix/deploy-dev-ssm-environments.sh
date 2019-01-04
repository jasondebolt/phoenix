#!/bin/bash
set -e

# Creates or updates AWS SSM Parameter for a dev environment.

# USAGE:
#   ./deploy-dev-ssm-environments.sh [create | update]
#
# EXAMPLES:
#   ./deploy-dev-ssm-environments.sh create
#   ./deploy-dev-ssm-environments.sh update

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-ssm-environments-params-dev.json`
STACK_NAME=$PROJECT_NAME-ssm-environments-$ENVIRONMENT
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

sed "s/VERSION_ID/$VERSION_ID/g" template-ssm-environments-params-dev.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json cloudformation > temp2.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-ssm-environments.json

aws cloudformation $1-stack \
    --stack-name $STACK_NAME \
    --template-body file://template-ssm-environments.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

# Cleanup
rm temp1.json
rm temp2.json
