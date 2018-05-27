#!/bin/bash
set -e

# Deploys a Jenkins instance.

# USAGE:
#   ./deploy-jenkins.sh
#
# DO NOT try to update this stack as a volume snapshot may not be automatically created.
# To update this stack, delete the current Jenkins stack, record the ID of the snapshot
# that gets automatically saved, and use the snapshot ID in the 'snapshotId' stack
# parameter before running this script to create a new jenkins stack retored with
# the previous volume.
#
# To see how this looks, look at the DeletionPolicy of the volume in the jenkins template:
#
#     "VarLibJenkins": {
#      "DeletionPolicy": "Snapshot",
#       ...
#
# EXAMPLES:
#   ./deploy-jenkins.sh
#
#   Where,
#     version_id is the number at the end of the stack name.

# Extract JSON properties for a file into a local variable
PROJECT_NAME=$(aws ssm get-parameter --name project-name | jq '.Parameter.Value' | sed -e s/\"//g)
DNS_PREFIX=$(jq -r '.Parameters.DnsPrefix' template-jenkins-params.json)

# Check for valid arguments
if [ $# -ne 0 ];
  then
    echo "Incorrect number of arguments supplied. This script takes no arguments"
    exit 1
fi

# Regenerate the params file into a format the the CloudFormation CLI expects.
python parameters_generator.py template-jenkins-params.json cloudformation > temp1.json

# Validate the CloudFormation template before template execution.
aws cloudformation validate-template --template-body file://template-jenkins.json

# Create or update the CloudFormation stack with deploys your docker service to the Dev cluster.
aws cloudformation create-stack --stack-name $PROJECT_NAME-jenkins-$DNS_PREFIX \
    --template-body file://template-jenkins.json \
    --parameters file://temp1.json \
    --capabilities CAPABILITY_IAM

# Cleanup
rm temp1.json
