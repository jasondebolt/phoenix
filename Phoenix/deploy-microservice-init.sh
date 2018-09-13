#!/bin/bash
set -e

# Creates a complete microservice project.
#
# USAGE
#   ./deploy-microservice-init.sh

echo "Deploying the CloudFormation Macro"
./deploy-macro.sh create

echo "Deploying microservice"
./deploy-microservice.sh create

echo "Deploying merge request pipeline"
./deploy-merge-request-pipeline-api.sh create

echo "Deploying microservice cleanup"
./deploy-microservice-cleanup.sh create
