#!/bin/bash
set -e

# Creates a microservice project.
#
# USAGE
#   ./deploy-microservice.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Extract JSON properties for a file into a local variable
CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' ssm-microservice-params.json)
PROJECT_NAME=$(aws ssm get-parameter --name __microservice-phoenix-project-name | jq '.Parameter.Value' | sed -e s/\"//g)
STACK_NAME=$PROJECT_NAME-microservice
MICROSERVICE_BUCKET_NAME=$(aws ssm get-parameter --name __microservice-phoenix-bucket-name | jq '.Parameter.Value' | sed -e s/\"//g)

# Generate the MICROSERVICE bucket if it doesn't already exist
aws s3 mb s3://$MICROSERVICE_BUCKET_NAME
aws s3 sync . s3://$MICROSERVICE_BUCKET_NAME/cloudformation --exclude "*" --include "template-*.json" --delete

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-microservice.json

aws cloudformation $1-stack \
    --stack-name $STACK_NAME \
    --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-microservice.json \
    --capabilities CAPABILITY_NAMED_IAM \
    --enable-termination-protection \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME
