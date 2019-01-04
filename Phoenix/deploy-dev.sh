#!/bin/bash
set -e

# Deploys an entire dev environment and also forcefully deploys/converges the dev API environment.

# USAGE:
#   ./deploy-dev-environment.sh ..
#        [create |
#         update api-deploy {rest-api-id} {stage-name} ]
#
# EXAMPLES:
#   ./deploy-dev-environment.sh create
#   ./deploy-dev-environment.sh update api-deploy l1l5pcj1xc v0

# Extract JSON properties for a file into a local variable
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)
DOMAIN_NAME=$(jq -r '.Parameters.Domain' template-ssm-globals-macro-params.json)
ENVIRONMENT=`jq -r '.Parameters.Environment' template-api-deployment-params-dev.json`
API_DEPLOYMENT_STACK_NAME=$PROJECT_NAME-api-deployment-$ENVIRONMENT

if [ $1 == "create" ]
  then
    ./deploy-dev-ssm-environments.sh create
    ./deploy-dev-database.sh create
    ./deploy-dev-ec2.sh create
    ./deploy-dev-lambda.sh create
    ./deploy-dev-ecs-task-main.sh create ecs
    ./deploy-dev-api-custom-domain.sh create
    ./deploy-dev-api.sh create
    ./deploy-dev-api-deployment.sh create
fi

API_ID=$3
VERSION=$4

# 1. Generates Swagger file from an API gateway REST API.
# 2. Generates a ~/swagger_postman.json that can be imported into Postman for testing purposes.
# 3. Opens a local browser tab with API docs.
swagger_postman() {
  aws apigateway get-export --parameters extensions='apigateway' --rest-api-id $API_ID \
      --stage-name $VERSION --export-type swagger $HOME/swagger_integrations.json

  aws apigateway get-export --parameters extensions='postman' --rest-api-id $API_ID \
      --stage-name $VERSION --export-type swagger $HOME/swagger_postman.json

  spectacle ~/swagger_integrations.json --target-dir $HOME/swagger_out
  echo Open in your browser: file:///$HOME/swagger_out/index.html
  open file:///$HOME/swagger_out/index.html
}

# Deploy or redoploys an "API deployment" from the API associated with the existing rest-api-id
if [ $1 == "update" ] && [ $2 == "api-deploy" ]
  then
    ./deploy-dev-api.sh update
    ./deploy-dev-api-deployment.sh update # Calls the 'API internals' Lambda function which adds body template mappings.

    aws apigateway delete-base-path-mapping --domain-name $ENVIRONMENT.$DOMAIN_NAME --base-path $VERSION
    aws apigateway delete-stage --rest-api-id $API_ID --stage-name $VERSION
    aws apigateway delete-documentation-version --rest-api-id $API_ID --documentation-version $VERSION

    aws apigateway create-deployment --rest-api-id $API_ID --stage-name $VERSION
    aws apigateway create-documentation-version --rest-api-id $API_ID --stage-name $VERSION --documentation-version $VERSION
    aws apigateway create-base-path-mapping --domain-name $ENVIRONMENT.$DOMAIN_NAME --base-path $VERSION --rest-api-id $API_ID --stage $VERSION

    # The CloudFormation is super slow, hence the CLI calls above with do something similar but much faster.
    #./deploy-dev-api-deployment.sh delete
    #aws cloudformation wait stack-delete-complete --stack-name $API_DEPLOYMENT_STACK_NAME
    #./deploy-dev-api-deployment.sh create

    swagger_postman

    exit 1
fi
