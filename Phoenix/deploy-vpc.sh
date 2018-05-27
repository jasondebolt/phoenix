#!/bin/bash
set -e

# Creates or updates the Microservice VPC's.
#
# USAGE
#   ./deploy-vpc.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-vpc-params-dev.json cloudformation > temp_dev.json
python parameters_generator.py template-vpc-params-testing.json cloudformation > temp_testing.json
python parameters_generator.py template-vpc-params-prod.json cloudformation > temp_prod.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-vpc.json

# Create or update the dev VPC.
aws cloudformation $1-stack \
    --stack-name dev-vpc \
    --template-body file://template-vpc.json \
    --parameters file://temp_dev.json

# Create or update the testing VPC.
aws cloudformation $1-stack \
    --stack-name testing-vpc \
    --template-body file://template-vpc.json \
    --parameters file://temp_testing.json

# Create or update the prod VPC.
aws cloudformation $1-stack \
    --stack-name prod-vpc \
    --template-body file://template-vpc.json \
    --parameters file://temp_prod.json

# Cleanup
rm temp_dev.json
rm temp_testing.json
rm temp_prod.json
