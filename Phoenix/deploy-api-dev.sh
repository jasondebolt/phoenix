#!/bin/bash
set -e

# Deploys the latest API Gateway for the dev API Gateway stage.

# USAGE:
#   ./deploy-api-dev.sh [create | update]
#
# EXAMPLES:
#   ./deploy-api-dev.sh create
#   ./deploy-api-dev.sh update

# Extract JSON properties for a file into a local variable
PROJECT_NAME=$(aws ssm get-parameter --name /microservice/credit-service/global/project-name | jq '.Parameter.Value' | sed -e s/\"//g)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-api-params-dev.json`
LAMBDA_BUCKET_NAME=$(aws ssm get-parameter --name /microservice/credit-service/global/lambda-bucket-name | jq '.Parameter.Value' | sed -e s/\"//g)
MICROSERVICE_BUCKET_NAME=$(aws ssm get-parameter --name /microservice/credit-service/global/bucket-name | jq '.Parameter.Value' | sed -e s/\"//g)
# Allow developers to name the environment whatever they want, supporting multiple dev environments.
VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

aws s3 cp template-api.json s3://$MICROSERVICE_BUCKET_NAME/cloudformation/

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-api.json

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" template-api-params-dev.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json cloudformation > temp2.json

STACK_NAME=$PROJECT_NAME-api-$ENVIRONMENT

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation $1-stack --stack-name $STACK_NAME \
    --template-url https://s3.amazonaws.com/$MICROSERVICE_BUCKET_NAME/cloudformation/template-api.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_IAM

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

# Cleanup
rm temp1.json
rm temp2.json
