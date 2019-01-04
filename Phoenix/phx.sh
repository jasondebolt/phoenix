#!/bin/bash

# Allows Phoenix commands/script to be executed on the same Docker container that your CodeBuild jobs use.

# Create the following bash alias in your ~/.bash_profile:
#   alias phx="./phx.sh"

# USAGE:
#  phx {any command} {any args}

# EXAMPLES:
#  phx aws s3 ls
#  phx ./deploy-dev-database.sh update
#  phx python generage_dev_params.py {your username}
#  phx python search_and_replace.py . {search string} {replace string}

# Check if jq utility is installed
package_name=jq
t=`which $package_name`
[ -z "$t" ] && echo "the $package_name isn't installed! Install with 'brew install jq'" && exit 1

IMAGE_ID=$(jq -r '.Parameters.CodeBuildDockerImage' template-ssm-globals-macro-params.json)

#$(aws ecr get-login --no-include-email --region us-east-1) && docker pull $IMAGE_ID && exit 1

docker run --privileged -it \
    --workdir /root/phx \
    -v ~/.aws:/root/.aws \
    -v $PWD:/root/phx $IMAGE_ID $@
