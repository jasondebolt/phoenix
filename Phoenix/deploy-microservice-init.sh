#!/bin/bash
set -e

# Creates a complete microservice project.
#
# For details on the {GitHub token} argument, see the deploy-github-access-token.sh script.
#
# USAGE
#   ./deploy-microservice-init.sh {GitHub token}

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in a Githab access token. See the 'deploy-github-access-token.sh' script."
    exit 1
fi

echo "Deploying GitHub token to SSM Parameter Store"
#./deploy-github-access-token.sh $1

echo "Deploying ACM SSL Certificates"
./deploy-acm-certificates.sh create

echo "Deploying S3 buckets and ECR repos"
./deploy-s3-ecr.sh create

echo "Deploying global SSM parameters and CloudFormation Macro"
./deploy-ssm-globals-macro.sh create

echo "Deploying pipeline"
./deploy-pipeline.sh create

echo "Deploying pull request webhook"
./deploy-github-webhook-pull-request.sh create

echo "Deploying release webhook"
echo "If you require release environments, add environments to 'ReleaseEnvironments' param in template-ssm-globals-macro-params.json"
./deploy-github-webhook-release.sh create

echo "Deploying microservice cleanup"
./deploy-microservice-cleanup.sh create
