#!/bin/bash
set -e

# Checks out a new git branch and create a review code pipeline on the branch.

# USAGE:
#   ./deploy-git-branch-and-pipeline.sh {branch_name}
#
# EXAMPLES:
#   ./deploy-git-branch-and-pipeline.sh fix-it-someday

BRANCH_NAME=$1

# Create a new git branch
git checkout -b $BRANCH_NAME

# Generate the param files
python generate_dev_params.py $BRANCH_NAME

# Create the Cloudformation stack
# Let Lambda do this. Do not uncomment the following line.
#/bin/bash deploy-code-pipeline-review-dev.sh create

git push origin $BRANCH_NAME
