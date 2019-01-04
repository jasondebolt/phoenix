#!/bin/bash
set -e

# Saves a GitHub access token to SSM parameter store for your project.
# You must generate an access token within GitHub and pass it to this script.
# To generate a token, install pwgen locally and run 'pwgen 32 -1'.
#
# This token is used in the following ways:
#  - To create the webhook associated with the main pipeline of your project.
#  - To create any other webhooks (pull requests, releases, etc.)
#  - Making GitHub API calls through Lambda Custom Resources within CloudFormation templates.
#
# When creating the webhook in GitHub, give it a name like "{YourProjectName}lineWebhook"
# and give in the "repo" and "admin:repo_hook" scopes. Also be sure to select "Enable SSO"
# and then "Authorize" else the token will not work.
#
# USAGE
#   ./deploy-github-access-token.sh {Github Token}

# Check for valid arguments
if [ $# -ne 1 ]
  then
    echo "Incorrect number of arguments supplied. Pass in a Githab access token"
    exit 1
fi

# Extract JSON properties for a file into a local variable
PROJECT_NAME=$(jq -r '.Parameters.ProjectName' template-ssm-globals-macro-params.json)

aws ssm put-parameter \
  --name /microservice/$PROJECT_NAME/global/github/access-token \
  --description 'GitHub access token used by this project' \
  --key-id 'alias/aws/ssm' \
  --type 'SecureString' \
  --overwrite \
  --value $1
