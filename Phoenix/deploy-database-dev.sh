#!/bin/bash
set -e

# Creates or updates the database layer.
#
# In this stack, the database passwords are automatically generated in Lambda,
# encrypted, and stored in AWS SSM Parameter Store for later retrieval.
#
# The password in returned to the CloudFormation stack and used in the MasterUserPassword
# parameter. All authored EC2 instances, ECS containers, etc. can then use the project
# KMS Key found in the microservice stack to decrypt the MasterPassword and
# initiate a database connection
#
# USAGE
#   ./deploy-database.sh [create | update]

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Extract JSON properties for a file into a local variable
PROJECT_NAME=`jq -r '.Parameters.ProjectName' template-microservice-params.json`
ENVIRONMENT=`jq -r '.Parameters.Environment' template-database-params-dev.json`
LAMBDA_BUCKET_NAME=`jq -r '.Parameters.LambdaBucketName' template-microservice-params.json`
# Allow developers to name the environment whatever they want, supporting multiple dev environments.
VERSION_ID=$ENVIRONMENT

# Upload the Lambda functions
listOfLambdaFunctions='password_generator'
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

# Replace the VERSION_ID string in the dev params file with the $VERSION_ID variable
sed "s/VERSION_ID/$VERSION_ID/g" template-database-params-dev.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json > temp2.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-database.json

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation $1-stack --stack-name $PROJECT_NAME-database-$ENVIRONMENT \
    --template-body file://template-database.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_IAM

# Cleanup
rm temp1.json
rm temp2.json
rm -rf builds
