#!/bin/bash
set -e

# Creates AWS Certificate Manager SSL certificates.
#
# USAGE
#   ./deploy-acm-certificates.sh [create | update]

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
DOMAIN=$(jq -r '.Parameters.Domain' template-ssm-globals-macro-params.json)
STACK_NAME=$PROJECT_NAME-acm-certificates
ENVIRONMENT='all'
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-acm-certificates.json

aws cloudformation $1-stack \
    --stack-name $STACK_NAME \
    --template-body file://template-acm-certificates.json \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        ParameterKey=Domain,ParameterValue=$DOMAIN \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

if [[ $1 == 'create' ]]; then
  aws cloudformation update-termination-protection --enable-termination-protection --stack-name $STACK_NAME
fi
