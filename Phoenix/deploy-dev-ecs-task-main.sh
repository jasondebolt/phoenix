#!/bin/bash
set -e

# Generates a random docker image tag, builds a docker image,
# updates the CloudFormation parameters file with the new image tag,
# and either creates or updates a CloudFormation stack which
# deploys the locally build docker image to the Dev ECS cluster in AWS.

# USAGE:
#   ./deploy-dev-ecs-task-main.sh [create | update] [sbt | location of docker file]
#
# EXAMPLES:
#   ./deploy-dev-ecs-task-main.sh update sbt --> Always use this command for Play/SBT projects.
#   ./deploy-dev-ecs-task-main.sh update .   --> Dockerfile in project root dir.
#   ./deploy-dev-ecs-task-main.sh update ecs   --> Dockerfile in ecs dir.

# Check for valid arguments
if [ $# -ne 2 ]
  then
    echo "Incorrect number of arguments supplied. Pass in either 'create' or 'update' and the location of the docker file"
    exit 1
fi

# Convert create/update to uppercase
OP=$(echo $1 | tr '/a-z/' '/A-Z/')

if [ -d "builds" ]; then
  echo deleting builds dir
  rm -rf builds
fi

ECS_PARAM_FILE='template-ecs-task-main-params-dev.json'
ECS_FILE='template-ecs-task.json'
TASK_FAMILY='main'

AWS_ACCOUNT_ID=`aws sts get-caller-identity --output text --query Account`
AWS_REGION=`aws configure get region`

CLOUDFORMATION_ROLE=$(jq -r '.Parameters.IAMRole' template-ssm-globals-macro-params.json)
ORGANIZATION_NAME=$(jq -r '.Parameters.OrganizationName' template-ssm-globals-macro-params.json)
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
LAMBDA_BUCKET_NAME=$ORGANIZATION_NAME-$PROJECT_NAME-lambda

ENVIRONMENT=`jq -r '.Parameters.Environment' $ECS_PARAM_FILE`
STACK_NAME=$PROJECT_NAME-ecs-$TASK_FAMILY-$ENVIRONMENT
# Allow developers to name the environment whatever they want, supporting multiple dev environments.
IMAGE_TAG=$TASK_FAMILY-$ENVIRONMENT-`date +"%Y-%m-%d-%H%M%S"`
IMAGE_NAME=$PROJECT_NAME-$TASK_FAMILY
ECR_REPO=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

VERSION_ID=$ENVIRONMENT-`date '+%Y-%m-%d-%H%M%S'`
CHANGE_SET_NAME=$VERSION_ID

# Upload the Python Lambda functions
listOfPythonLambdaFunctions='password_generator'
for functionName in $listOfPythonLambdaFunctions
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
sed "s/VERSION_ID/$VERSION_ID/g" $ECS_PARAM_FILE > temp1.json

if [ $2 == "sbt" ]
  then
    echo 'SBT docker build'
    # This is a Play app, so use sbt to build the docker image
    cd ../
    sbt docker:stage
    docker build -t $ECR_REPO server/target/docker/stage
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
sed "s/IMAGE_TAG/$IMAGE_TAG/g" temp1.json > temp2.json

# Regenerate the dev params file into a format the the CloudFormation CLI expects.
python parameters_generator.py temp2.json cloudformation > temp3.json

# Make macro name unique in the AWS account:
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
sed "s/PROJECTNAMELambdaMacro/${PROJECT_NAME}LambdaMacro/g" $ECS_FILE > temp0.json
# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://temp0.json

aws cloudformation create-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME \
    --template-body file://temp0.json \
    --parameters file://temp3.json \
    --change-set-type $OP \
    --capabilities CAPABILITY_NAMED_IAM \
    --role-arn $CLOUDFORMATION_ROLE

aws cloudformation wait change-set-create-complete \
    --change-set-name $CHANGE_SET_NAME --stack-name $STACK_NAME

# Let's automatically execute the change-set for now
aws cloudformation execute-change-set --stack-name $STACK_NAME \
    --change-set-name $CHANGE_SET_NAME

aws cloudformation wait stack-$1-complete --stack-name $STACK_NAME

# Cleanup
rm temp1.json
rm temp2.json
rm temp3.json
