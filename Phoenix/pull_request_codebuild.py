""" Handles CodeBuild jobs executing in the context of a GitHub Pull Request

USAGE:
  python pull_request_codebuild.py [build | unit-test | lint]

  As long as you have the environment variables set as specified in the
  initializer, you can run this script either locally or on AWS CodeBuild.

  Within AWS CodeBuild, these environment variables will automatically be set
  from the 'template-pull-request-pipeline.json' CloudFormation stack, which
  is created by a Lambda function that is invoked by a GitHub webhook
  for pull request events.

  This script does the following:
    1) Persists a github.json file that is passed by CodePipeline to a Lambda function.
    2) Notifies GitHub of the status of AWS CodeBuild jobs.
    3) Generates an ECS parameter template specifically for spinning up
       a dev ECS instance used during code review.
"""

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

import os
import urllib
from urllib.parse import quote
import sys
import json
import requests

# These env variables are passed in via CloudFormation
PIPELINE_NAME = os.environ.get('PIPELINE_NAME')
GITHUB_ORGANIZATION = os.environ.get('GITHUB_ORGANIZATION')
REPO_NAME = os.environ.get('REPO_NAME')
SOURCE_BRANCH = os.environ.get('SOURCE_BRANCH')
PULL_REQUEST_NUMBER = os.environ.get('PULL_REQUEST_NUMBER')

# These env variables are sometimes made avaialable in codebuild
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')

# These env variables are always avaialable in AWS CodeBuild
CODEBUILD_BUILD_ARN = os.environ.get('CODEBUILD_BUILD_ARN')
CODE_BUILD_REGION = os.environ.get('AWS_DEFAULT_REGION')
CODEBUILD_BUILD_SUCCEEDING = int(os.environ.get('CODEBUILD_BUILD_SUCCEEDING', 0))
CODEBUILD_RESOLVED_SOURCE_VERSION = os.environ.get('CODEBUILD_RESOLVED_SOURCE_VERSION')
BUILD_NAME = CODEBUILD_BUILD_ARN.split(':')[-2].split('/')[1]
BUILD_ID = CODEBUILD_BUILD_ARN.split(':')[-1]

# GitHub vars
GITHUB_API_URL = 'https://api.github.com'

def get_code_build_url():
    return (
        'https://console.aws.amazon.com/codebuild/home?region={region}'
        '#/builds/{build_name}:{build_id}/view/new').format(
            region=CODE_BUILD_REGION, build_name=BUILD_NAME, build_id=BUILD_ID)

def generate_ssm_params():
    print("Saving updated SSM parameter file...")
    file_path = os.path.join(
        os.environ.get('CODEBUILD_SRC_DIR'), 't-ssm-environments-params-testing.json'
    )
    ssm_params = _parse_json(file_path)
    print(json.dumps(ssm_params, indent=2))
    ssm_params['Parameters']['Environment'] = PIPELINE_NAME
    ssm_params['Parameters']['Description'] = 'A pull request environment is used for pull requests.'
    ssm_params_file = open('t-ssm-environments-params-testing.json', 'w')
    ssm_params_file.write(json.dumps(ssm_params, indent=2))

def generate_ec2_params():
    print("Saving updated ECS parameter file...")
    file_path = os.path.join(
        os.environ.get('CODEBUILD_SRC_DIR'), 't-ec2-params-testing.json'
    )
    ec2_params = _parse_json(file_path)
    print(json.dumps(ec2_params, indent=2))
    # We will use the testing environment by default, but the URL will include the git commit sha1.
    # Also, we will use the pipeline name as the environment.
    # If we used the git sha1 as the environment, a new EC2 instance would be created for every pull request update,
    # which is super slow an inefficient.
    # Ideally, we would spin up an EC2 instance when the MR is created, and tear it down when MR is pulld or closed.
    # The pipeline name a a good environment choice since that name persists throughout the MR.
    # NOTE!: If you change the below URL, you must also change this value in the post_pullrequests lambda function.
    ec2_params['Parameters']['Environment'] = PIPELINE_NAME
    ec2_params['Parameters']['DBEnvironment'] = 'dev'
    ec2_params['Parameters']['VPCPrefix'] = 'dev'
    ec2_params_file = open('t-ec2-params-testing.json', 'w')
    ec2_params_file.write(json.dumps(ec2_params, indent=2))

def generate_lambda_params():
    print("Saving updated Lambda parameter file...")
    file_path = os.path.join(
        os.environ.get('CODEBUILD_SRC_DIR'), 't-lambda-params-testing.json'
    )
    lambda_params = _parse_json(file_path)
    print(json.dumps(lambda_params, indent=2))
    lambda_params['Parameters']['Environment'] = PIPELINE_NAME
    lambda_params['Parameters']['VPCPrefix'] = 'dev'
    lambda_params_file = open('t-lambda-params-testing.json', 'w')
    lambda_params_file.write(json.dumps(lambda_params, indent=2))

def generate_ecs_task_main_params():
    print("Saving updated ECS task main parameter file...")
    file_path = os.path.join(
        os.environ.get('CODEBUILD_SRC_DIR'), 't-ecs-task-main-params-testing.json'
    )
    ecs_params = _parse_json(file_path)
    print(json.dumps(ecs_params, indent=2))
    # NOTE!: Comments in the 'generate_ec2_params' function above apply to this function as well.
    ecs_params['Parameters']['Environment'] = PIPELINE_NAME
    ecs_params['Parameters']['DBEnvironment'] = 'dev'
    ecs_params['Parameters']['VPCPrefix'] = 'dev'
    ecs_params['Parameters']['URLPrefixOverride'] = 'mr-{0}'.format(CODEBUILD_RESOLVED_SOURCE_VERSION)
    ecs_params_file = open('t-ecs-task-main-params-testing.json', 'w')
    ecs_params_file.write(json.dumps(ecs_params, indent=2))

def generate_lambda_github_config():
    print("Saving github.json file for the LambdaPostPullRequest lambda function to pick up.")
    github_obj = {
      'RepoName': REPO_NAME,
      'SourceBranch': SOURCE_BRANCH,
      'PullRequestNumber': PULL_REQUEST_NUMBER,
      'SourceVersion': CODEBUILD_RESOLVED_SOURCE_VERSION
    }
    github_lambda_config_file = open('github.json', 'w')
    github_lambda_config_file.write(json.dumps(github_obj, indent=2))

def _parse_json(path):
    result = open(os.path.join(sys.path[0], path), 'rb').read()
    try:
        return json.loads(result)
    except json.decoder.JSONDecodeError as e:
        print('\nYour JSON is not valid! Did you check trailing commas??\n')
        raise(e)

def send_status(build_type):
    # Build can can be 'build', 'lint', 'unit-test', etc.
    url = os.path.join(
        GITHUB_API_URL, 'repos/{0}/{1}/statuses/{2}'.format(
            GITHUB_ORGANIZATION, REPO_NAME,
            CODEBUILD_RESOLVED_SOURCE_VERSION))
    payload = {
        'state': 'success',
        'target_url': get_code_build_url(),
        'description': 'The {0} succeeded!'.format(build_type),
        'context': build_type
    }
    headers = {'Authorization': 'token {0}'.format(GITHUB_ACCESS_TOKEN)}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)
    print(json.dumps(response.json(), indent=2))


def onBuildJobCompletion():
    if CODEBUILD_BUILD_SUCCEEDING:
        send_status('build')
    # Save git github.json file
    generate_ssm_params()
    generate_ec2_params()
    generate_lambda_params()
    generate_ecs_task_main_params()
    generate_lambda_github_config()

def onUnitTestJobCompletion():
    if CODEBUILD_BUILD_SUCCEEDING:
        send_status('unit-test')

def onLintJobCompletion():
    if CODEBUILD_BUILD_SUCCEEDING:
        send_status('lint')

if __name__ == '__main__':
    # The github.json file is expected by the Lambda function that runs after pull request ECS container deployments.
    # Creating an empty github.json file here for cases where this is a non-pull request related build.
    # If this file is not created, the buildspec.yml file cause the 'build' CodeBuild job to fail since it is explicitly listed as an artifact.
    # See the 'generate_lambda_github_config()' function above for the real github.json file that will overwrite this file if this is a pull request build.
    github_lambda_config_file = open('github.json', 'w')
    github_lambda_config_file.write('')

    if len(sys.argv) != 2:
        print('You must pass in build, unit-test, or lint as an argument')
        sys.exit(0)
    # Any of the three following conditions may be met if this is a non-pull request build.
    if not GITHUB_ORGANIZATION:
        print('GITHUB_ORGANIZATION environment variable not set. This might be a non pull-request build.')
        sys.exit(0)
    if not REPO_NAME:
        print('REPO_NAME environment variable not set. This might be a non pull-request build.')
        sys.exit(0)
    if not SOURCE_BRANCH:
        print('SOURCE_BRANCH environment variable not set. This might be a non pull-request build.')
        sys.exit(0)
    if not PULL_REQUEST_NUMBER:
        print('PULL_REQUEST_NUMBER environment variable not set. This might be a non pull-request build.')
        sys.exit(0)
    if not GITHUB_ACCESS_TOKEN:
        print('No GITHUB_ACCESS_TOKEN environment variable has been set!')
        sys.exit(0)

    arg = sys.argv[1]

    if arg == 'build':
        if not PIPELINE_NAME:
            print('PIPELINE_NAME environment variable not set. This might be a non pull-request build.')
            sys.exit(0)
        print('Running onBuildJobCompletion')
        onBuildJobCompletion()
    elif arg == 'unit-test':
        print('Running onUnitTestJobCompletion')
        onUnitTestJobCompletion()
    elif arg == 'lint':
        print('Running onLintJobCompletion')
        onLintJobCompletion()
    else:
        print('Unknown argument: {0}'.format(arg))
