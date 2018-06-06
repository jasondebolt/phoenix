""" Handles CodeBuild jobs executing in the context of a GitLab Merge Request

USAGE:
  python2.7 merge_request_codebuild.py [build | unit-test | lint]

  This script must be run using Python2.7 as that is the version of Python
  that is being used in our AWS CodeBuild environment.

  As long as you have the environment variables set as specified in the
  initializer, you can run this script either locally or on AWS CodeBuild.

  Within AWS CodeBuild, these environment variables will automatically be set
  from the 'template-merge-request-pipeline.json' CloudFormation stack, which
  is created by a Lambda function that is invoked by a GitLab webhook
  for merge request events.

  This script does the following:
    1) Notifies GitLab of the status of AWS CodeBuild jobs.
    2) Generates an ECS parameter template specifically for spinning up
       a dev ECS instance used during code review.
"""

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

import os
import urllib
import sys
import json
import requests

# These env variables are passed in via CloudFormation
PIPELINE_NAME = os.environ.get('PIPELINE_NAME')
GITLAB_PROJECT_ID = os.environ.get('GITLAB_PROJECT_ID')
MERGE_REQUEST_INTERNAL_ID = os.environ.get('MERGE_REQUEST_INTERNAL_ID')
REPO_NAME = os.environ.get('REPO_NAME')
SOURCE_BRANCH = os.environ.get('SOURCE_BRANCH')

# These env variables are sometimes made avaialable in codebuild
GITLAB_ACCESS_TOKEN = os.environ.get('GITLAB_ACCESS_TOKEN')
GITLAB_UNIT_TEST_ACCESS_TOKEN = os.environ.get('GITLAB_UNIT_TEST_ACCESS_TOKEN')
GITLAB_LINT_ACCESS_TOKEN = os.environ.get('GITLAB_LINT_ACCESS_TOKEN')
GITLAB_URL = os.environ.get('GITLAB_URL', '')

# These env variables are always avaialable in AWS CodeBuild
CODE_BUILD_ARN = os.environ.get('CODEBUILD_BUILD_ARN')
CODE_BUILD_REGION = os.environ.get('AWS_DEFAULT_REGION')
CODEBUILD_BUILD_SUCCEEDING = int(os.environ.get('CODEBUILD_BUILD_SUCCEEDING', 0))
CODEBUILD_RESOLVED_SOURCE_VERSION = os.environ.get('CODEBUILD_RESOLVED_SOURCE_VERSION')
BUILD_NAME = CODE_BUILD_ARN.split(':')[-2].split('/')[1]
BUILD_ID = CODE_BUILD_ARN.split(':')[-1]
BUILD_EMOJI = ':thumbsup:' if CODEBUILD_BUILD_SUCCEEDING else ':bangbang:'

# Gitlab vars
GITLAB_API_URL = os.path.join(GITLAB_URL, 'api/v4/projects')

def get_code_build_url():
    return (
        'https://console.aws.amazon.com/codebuild/home?region={region}'
        '#/builds/{build_name}:{build_id}/view/new').format(
            region=CODE_BUILD_REGION, build_name=BUILD_NAME, build_id=BUILD_ID)

def merge_request_note(emoji):
    body = (
        '<a href="{code_build_url}">{build_name}</a> &nbsp; &nbsp; {emoji} '
        '@ commit {source_version}').format(
            code_build_url=get_code_build_url(), build_name=BUILD_NAME,
            emoji=emoji, source_version=CODEBUILD_RESOLVED_SOURCE_VERSION)
    return urllib.quote(body)

def merge_request_note_url(body):
    return os.path.join(
        GITLAB_API_URL, GITLAB_PROJECT_ID, 'merge_requests',
        MERGE_REQUEST_INTERNAL_ID, 'notes?body={0}'.format(body))

def merge_request_approval_url():
    return os.path.join(
        GITLAB_API_URL, GITLAB_PROJECT_ID, 'merge_requests',
        MERGE_REQUEST_INTERNAL_ID, 'approve')

class RequestSender(object):
    def __init__(self, token):
        self.token = token
    def send_request(self, url):
        print('Posting to {0}'.format(url))
        headers = {'Private-Token': self.token}
        response = requests.post(url, headers=headers)
        print(response)

def generate_ecs_params():
    print("Saving updated ECS parameter file...")
    file_path = os.path.join(
        os.environ.get('CODEBUILD_SRC_DIR'), 't-ecs-params-testing.json'
    )
    ecs_params = _parse_json(file_path)
    print(json.dumps(ecs_params, indent=2))
    # We will use the testing environment by default, but the URL will include the git commit sha1.
    # Also, we will use the pipeline name as the environment.
    # If we left the 'Environment' parameter value as the default of 'testing', the underlying EC2
    # instance would fail to launch as a 'testing' instance already exists.
    # If we used the git sha1 as the environment, a new EC2 instance would be created for every merge request update,
    # which is super slow an inefficient.
    # Ideally, we would spin up an EC2 instance when the MR is created, and tear it down when MR is merged or closed.
    # The pipeline name a a good environment choice since that name persists throughout the MR.
    # NOTE!: If you change the below URL, you must also change this value in the post_mergerequests lambda function.
    ecs_params['Parameters']['Environment'] = PIPELINE_NAME
    ecs_params['Parameters']['URLPrefixOverride'] = 'mr-{0}'.format(CODEBUILD_RESOLVED_SOURCE_VERSION)
    ecs_params_file = open('t-ecs-params-testing.json', 'w')
    ecs_params_file.write(json.dumps(ecs_params, indent=2))

def generate_lambda_gitlab_config():
    print("Saving gitlab.json file for the LambdaPostMergeRequest lambda function to pick up.")
    gitlab_obj = {
      'RepoName': REPO_NAME,
      'SourceBranch': SOURCE_BRANCH,
      'MergeRequestId': MERGE_REQUEST_INTERNAL_ID,
      'SourceVersion': CODEBUILD_RESOLVED_SOURCE_VERSION,
      'ProjectId': GITLAB_PROJECT_ID
    }
    gitlab_lambda_config_file = open('gitlab.json', 'w')
    gitlab_lambda_config_file.write(json.dumps(gitlab_obj, indent=2))

def _parse_json(path):
    result = open(os.path.join(sys.path[0], path), 'rb').read()
    try:
        return json.loads(result)
    except json.decoder.JSONDecodeError as e:
        print('\nYour JSON is not valid! Did you check trailing commas??\n')
        raise(e)

def onBuildJobCompletion():
    sender = RequestSender(GITLAB_ACCESS_TOKEN)
    # Approve the merge request from a build perspective
    if CODEBUILD_BUILD_SUCCEEDING:
        sender.send_request(merge_request_approval_url())
    # Notify GitLab of the approval
    sender.send_request(merge_request_note_url(merge_request_note(BUILD_EMOJI)))
    # Generate the ECS CloudFormation stack to create an ECS instance
    generate_ecs_params()
    generate_lambda_gitlab_config()

def onUnitTestJobCompletion():
    sender = RequestSender(GITLAB_UNIT_TEST_ACCESS_TOKEN)
    # Approve the merge request from a unit test perspective
    if CODEBUILD_BUILD_SUCCEEDING:
        sender.send_request(merge_request_approval_url())
    # Notify GitLab of the approval
    sender.send_request(merge_request_note_url(merge_request_note(BUILD_EMOJI)))

def onLintJobCompletion():
    sender = RequestSender(GITLAB_LINT_ACCESS_TOKEN)
    # Approve the merge request from a lint perspective
    if CODEBUILD_BUILD_SUCCEEDING:
        sender.send_request(merge_request_approval_url())
    # Notify GitLab of the approval
    sender.send_request(merge_request_note_url(merge_request_note(BUILD_EMOJI)))

if __name__ == '__main__':
    # The gitlab.json file is expected by the Lambda function that runs after merge request ECS container deployments.
    # Creating an empty gitlab.json file here for cases where this is a non-merge request related build.
    # If this file is not created, the buildspec.yml file cause the 'build' CodeBuild job to fail since it is explicitly listed as an artifact.
    # See the 'generate_lambda_gitlab_config()' function above for the real gitlab.json file that will overwrite this file if this is a merge request build.
    gitlab_lambda_config_file = open('gitlab.json', 'w')
    gitlab_lambda_config_file.write('')

    if len(sys.argv) != 2:
        print('You must pass in build, unit-test, or lint as an argument')
        sys.exit(0)
    # Any of the three following conditions may be met if this is a non-merge request build.
    if not GITLAB_PROJECT_ID:
        print('GITLAB_PROJECT_ID environment variable not set. This might be a non merge-request build.')
        sys.exit(0)
    if not MERGE_REQUEST_INTERNAL_ID:
        print('MERGE_REQUEST_INTERNAL_ID environment variable not set. This might be a non merge-request build.')
        sys.exit(0)
    if not REPO_NAME:
        print('REPO_NAME environment variable not set. This might be a non merge-request build.')
        sys.exit(0)
    if not SOURCE_BRANCH:
        print('SOURCE_BRANCH environment variable not set. This might be a non merge-request build.')
        sys.exit(0)
    if not GITLAB_URL:
        print('GITLAB_URL environment variable not set. This might be a non merge-request build.')
        sys.exit(0)

    arg = sys.argv[1]

    if arg == 'build':
        if not GITLAB_ACCESS_TOKEN:
            print('No GITLAB_ACCESS_TOKEN environment variable has been set!')
            sys.exit(0)
        if not PIPELINE_NAME:
            print('PIPELINE_NAME environment variable not set. This might be a non merge-request build.')
            sys.exit(0)
        print('Running onBuildJobCompletion')
        onBuildJobCompletion()
    elif arg == 'unit-test':
        if not GITLAB_UNIT_TEST_ACCESS_TOKEN:
            print('No GITLAB_UNIT_TEST_ACCESS_TOKEN environment variable has been set!')
            sys.exit(0)
        print('Running onUnitTestJobCompletion')
        onUnitTestJobCompletion()
    elif arg == 'lint':
        if not GITLAB_LINT_ACCESS_TOKEN:
            print('No GITLAB_LINT_ACCESS_TOKEN environment variable has been set!')
            sys.exit(0)
        print('Running onLintJobCompletion')
        onLintJobCompletion()
    else:
        print('Unknown argument: {0}'.format(arg))
