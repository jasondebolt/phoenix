#!/bin/bash
set -e

# Creates or updates AWS ECS resources required to run one or more ECS tasks/services.

# USAGE:
#   ./deploy-dev-ec2.sh [create | update]
#
# EXAMPLES:
#   ./deploy-dev-ec2.sh create
#   ./deploy-dev-ec2.sh update

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Convert create/update to uppercase
OP=$(echo $1 | tr '/a-z/' '/A-Z/')

CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-ec2-params-dev.json`
STACK_NAME=$PROJECT_NAME-ec2-$ENVIRONMENT
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-ec2-params-dev.json cloudformation > temp1.json

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" template-ec2.json > temp0.json
# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://temp0.json

aws cloudformation create-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME \
    --template-body file://temp0.json \
    --parameters file://temp1.json \
    --change-set-type $OP \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait change-set-create-complete \
    --change-set-name $CHANGE_SET_NAME --stack-name $STACK_NAME

# Let's automatically execute the change-set for now
aws cloudformation execute-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

# Cleanup
rm temp1.json
