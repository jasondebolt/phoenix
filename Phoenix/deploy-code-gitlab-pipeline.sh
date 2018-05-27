#!/bin/bash
set -e

# https://aws.amazon.com/blogs/devops/integrating-git-with-aws-codepipeline/
# Deploys an API Gateway --> Lambda --> S3 pipeline for streaming master branch pushes to an S3 bucket.
# 54.175.38.99/32 is the IP address of the NAT instance in front of our GitLab instance.
#
# USAGE:
#  ./deploy-gitlab-pipeline.sh [create | update]


# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update'."
    exit 1
fi

# Extract JSON properties for a file into a local variable
PROJECT_NAME=`jq -r '.Parameters.ProjectName' template-microservice-params.json`
API_SECRET=`pwgen 32 -1`
VERSION_ID=`echo $((1 + RANDOM % 10000))`

# Replace the API_SECRET string in the dev params file with the $API_SECRET variable
sed "s/API_SECRET/$API_SECRET/g" template-gitlab-pipeline-params.json > temp1.json
sed "s/VERSION_ID/$VERSION_ID/g" temp1.json > temp2.json

python parameters_generator.py temp2.json cloudformation > temp3.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-gitlab-pipeline.json

aws cloudformation $1-stack \
    --stack-name $PROJECT_NAME-gitlab-pipeline-$VERSION_ID \
    --template-body file://template-gitlab-pipeline.json \
    --parameters file://temp3.json \
    --capabilities CAPABILITY_IAM

# Cleanup
rm temp1.json
rm temp2.json
rm temp3.json

echo ================ API SECRET ==================
echo $API_SECRET
