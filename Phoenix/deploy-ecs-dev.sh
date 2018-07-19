#!/bin/bash
set -e

# Creates or updates AWS ECS resources required to run one or more ECS tasks/services.

# USAGE:
#   ./deploy-ecs-dev.sh [create | update]
#
# EXAMPLES:
#   ./deploy-ecs-dev.sh create
#   ./deploy-ecs-dev.sh update

AWS_ACCOUNT_ID=`aws sts get-caller-identity --output text --query Account`
AWS_REGION=`aws configure get region`
PROJECT_NAME=$(aws ssm get-parameter --name /microservice/phoenix/project-name | jq '.Parameter.Value' | sed -e s/\"//g)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-ecs-params-dev.json`

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-ecs-params-dev.json cloudformation > temp1.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-ecs.json

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation $1-stack --stack-name $PROJECT_NAME-ecs-$ENVIRONMENT \
    --template-body file://template-ecs.json \
    --parameters file://temp1.json \
    --capabilities CAPABILITY_NAMED_IAM

# Cleanup
rm temp1.json
