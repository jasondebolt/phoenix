#!/bin/bash
set -e

# Generates a random docker image tag, builds a docker image,
# updates the CloudFormation parameters file with the new image tag,
# and either creates or updates a CloudFormation stack which
# deploys the locally build docker image to the Dev ECS cluster in AWS.

# USAGE:
#   ./deploy-ecs-dev.sh [create | update] [sbt | location of docker file]
#
# EXAMPLES:
#   ./deploy-ecs-dev.sh update sbt --> Always use this command for Play/SBT projects.
#   ./deploy-ecs-dev.sh update .   --> Dockerfile in project root dir.
#   ./deploy-ecs-dev.sh update ecs   --> Dockerfile in ecs dir.

AWS_ACCOUNT_ID=`aws sts get-caller-identity --output text --query Account`
AWS_REGION=`aws configure get region`
PROJECT_NAME=$(aws ssm get-parameter --name microservice-project-name | jq '.Parameter.Value' | sed -e s/\"//g)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-ecs-params-dev.json`
# Allow developers to name the environment whatever they want, supporting multiple dev environments.
IMAGE_TAG=$ENVIRONMENT-`date +"%Y-%m-%d-%H%M%S"`

IMAGE_NAME=$PROJECT_NAME
ECR_REPO=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG


# Check for valid arguments
if [ $# -ne 2 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update' and the location of the docker file"
    exit 1
fi

if [ $2 == "sbt" ]
  then
    echo 'SBT docker build'
    # This is a Play app, so use sbt to build the docker image
    cd ../
    cp build.sbt build.sbt.backup
    sed "s/IMAGE_TAG/$IMAGE_TAG/g" build.sbt > temp.sbt && mv temp.sbt build.sbt
    sbt docker:publishLocal
    # Restore original sbt file.
    cp build.sbt.backup build.sbt
    rm build.sbt.backup
    cd Phoenix
else
  # This is a regular non-play app, so we use docker build directly.
  echo 'docker build'
  docker build -t $ECR_REPO $2
fi

# Obtain auth with AWS Elastic Container Rep
eval $(aws ecr get-login --no-include-email --region $AWS_REGION)

# Push the local docker image to AWS Elastic Container Repo
docker push $ECR_REPO

# Replace the IMAGE_TAG string in the dev params file with the $IMAGE_TAG variable
sed "s/IMAGE_TAG/$IMAGE_TAG/g" template-ecs-params-dev.json > temp1.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp1.json cloudformation > temp2.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-ecs.json

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation $1-stack --stack-name $PROJECT_NAME-ecs-$ENVIRONMENT \
    --template-body file://template-ecs.json \
    --parameters file://temp2.json \
    --capabilities CAPABILITY_NAMED_IAM

# Cleanup
rm temp1.json
rm temp2.json
