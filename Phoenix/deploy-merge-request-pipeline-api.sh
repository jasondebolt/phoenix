#!/bin/bash
set -e

# Deploys a merge request API Gateway endpoint and Lambda handler to dynamically generate merge request pipelines.

# USAGE:
#   ./deploy-merge-request-pipeline-api.sh [create | update]
#
# EXAMPLES:
#   ./deploy-merge-request-pipeline-api.sh create
#   ./deploy-merge-request-pipeline-api.sh update

# Extract JSON properties for a file into a local variable
PROJECT_NAME=$(aws ssm get-parameter --name microservice-project-name | jq '.Parameter.Value' | sed -e s/\"//g)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-merge-request-pipeline-api-params.json`
LAMBDA_BUCKET_NAME=$(aws ssm get-parameter --name microservice-lambda-bucket-name | jq '.Parameter.Value' | sed -e s/\"//g)
VERSION_ID=`jq -r '.Parameters.Version' template-merge-request-pipeline-api-params.json`
# Allow developers to name the environment whatever they want, supporting multiple dev environments.

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Upload the Lambda functions
listOfLambdaFunctions='mergerequests post_mergerequests'
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
python parameters_generator.py template-merge-request-pipeline-api-params.json cloudformation > temp1.json

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" temp1.json > temp2.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-merge-request-pipeline-api.json

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation $1-stack --stack-name $PROJECT_NAME-merge-request-pipeline-api-$ENVIRONMENT \
    --template-body file://template-merge-request-pipeline-api.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_IAM

# Cleanup
rm temp1.json
rm temp2.json
