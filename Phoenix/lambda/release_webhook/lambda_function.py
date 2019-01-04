import os
import json
import boto3
import botocore
import requests
from datetime import datetime
import urllib.parse
import hmac
import re
import base64

# Handler for receiving release events from GitHub.

# https://developer.github.com/v3/activity/events/types/#pushevent

cloudformation_client = boto3.client('cloudformation')
ssm_client = boto3.client('ssm')

GITHUB_API_URL = 'https://api.github.com'

class JSONObject:
  def __init__(self, dict):
      vars(self).update(dict)

# Assign python values to values return from gitlab JSON reqeuest object
false = False
true = True
null = None

def get_github_access_token():
    print('getting github access token')
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/github/access-token'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_github_release_secret():
    print('getting github release secret')
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/github/release-secret'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_microservice_bucket_name():
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/bucket-name'.format(os.environ['PROJECT_NAME']),
        WithDecryption=False
    )
    return response['Parameter']['Value']


def get_release_environments():
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/release-environments'.format(os.environ['PROJECT_NAME']),
        WithDecryption=False
    )
    result = response['Parameter']['Value']
    return [val.strip() for val in result.split(',')]  # ['staging', 'qa', ...]


def create_or_update_stack(create, stack_name, template_url, parameters):
    if create:
        response = cloudformation_client.create_stack(
          StackName=stack_name,
          TemplateURL=template_url,
          Parameters=parameters,
          Capabilities=['CAPABILITY_IAM']
        )
    else:
        response = cloudformation_client.update_stack(
          StackName=stack_name,
          TemplateURL=template_url,
          Parameters=parameters,
          Capabilities=['CAPABILITY_IAM']
        )


def delete_stack_if_exists(stack_name):
    # Idempotent way to delete a CloudFormation stack.
    try:
        print('Attempting to delete stack {0}'.format(stack_name))
        response = cloudformation_client.delete_stack(StackName=stack_name)
        return response
    except Exception as e:
        print('Error: {0}'.format(e))
        print('Stack {0} may not exist. Skipping delete.'.format(stack_name))


def success_response():
    return {
        "isBase64Encoded" : "false",
        "statusCode": "200",
        "headers": {},
        "body": "Success!"
    }

def lambda_handler(event, context):
    print(event)

    # I used Lambda proxy integration here.
    github_signature = event['headers']['X-Hub-Signature']
    secret = get_github_release_secret()
    signature = hmac.new(secret.encode(), event['body'].encode(), "sha1")
    expected_signature = 'sha1=' + signature.hexdigest()

    print('github_signature: ', github_signature)
    print('expected_signature: ', expected_signature)

    if not hmac.compare_digest(github_signature, expected_signature):
        return {
            "isBase64Encoded" : "false",
            "statusCode": "401",
            "headers": {},
            "body": "Unauthorized!"
        }
    else:
        # For a full list of events: https://developer.github.com/v3/activity/events/types/#pushevent
        print('EVENT:')
        print(event)
        json_obj = json.dumps(event, indent=4)
        print('JSON_OBJECT:')
        print(json_obj)
        obj = json.loads(json_obj, object_hook=JSONObject)
        print('OBJECT:')
        print(obj)
        body = json.loads(obj.body, object_hook=JSONObject)
        print('BODY:')
        print(body)

        if not hasattr(body, 'pusher'):
            raise Exception('Object is not a push request!')

        repo_name = body.repository.name
        _, ref_type, ref_name = body.ref.split("/")
        is_tag, is_branch = ref_type == "tags", ref_type == "heads"
        if not is_branch:
            return success_response()

        is_create_branch_push_event = body.before == '0000000000000000000000000000000000000000'
        is_delete_branch_push_event = body.after == '0000000000000000000000000000000000000000'
        print('is_create_branch_push_event: ', is_create_branch_push_event)
        print('is_delete_branch_push_event: ', is_delete_branch_push_event)

        # Branch name is the 'ref_name'
        is_release_branch = bool(re.match('release-\d{8}$', ref_name))
        print('is_release_branch: ', is_release_branch)

        if not is_release_branch:
            # We only care about release branches.
            return success_response()

        release_environments = get_release_environments()

        for release_environment in release_environments:
            stack_name = '{repo_name}-{release_environment}-{source_branch}'.format(
                repo_name=repo_name, release_environment=release_environment,
                source_branch=ref_name.replace('_', '-')
            )

            template_name = 'template-release-environment-pipeline.json'
            template_url = 'https://s3.amazonaws.com/{0}/cloudformation/{1}'.format(
                get_microservice_bucket_name(), template_name)

            parameters=[
                {'ParameterKey': 'ProjectName', 'ParameterValue': os.environ['PROJECT_NAME']},
                {'ParameterKey': 'ProjectDescription', 'ParameterValue': os.environ['PROJECT_DESCRIPTION']},
                {'ParameterKey': 'CodePipelineBucketName', 'ParameterValue': os.environ['CODE_PIPELINE_BUCKET_NAME']},
                {'ParameterKey': 'CodeBuildDockerImage', 'ParameterValue': os.environ['CODE_BUILD_DOCKER_IMAGE']},
                {'ParameterKey': 'CodeBuildServiceRoleArn', 'ParameterValue': os.environ['CODE_BUILD_SERVICE_ROLE_ARN']},
                {'ParameterKey': 'CodePipelineServiceRoleArn', 'ParameterValue': os.environ['CODE_PIPELINE_SERVICE_ROLE_ARN']},
                {'ParameterKey': 'LambdaBucketName', 'ParameterValue': os.environ['LAMBDA_BUCKET_NAME']},
                {'ParameterKey': 'PipelineName', 'ParameterValue': stack_name},
                {'ParameterKey': 'GitHubOrganization', 'ParameterValue': os.environ['GITHUB_ORGANIZATION']},
                {'ParameterKey': 'RepoName', 'ParameterValue': repo_name},
                {'ParameterKey': 'SourceBranch', 'ParameterValue': ref_name},
                {'ParameterKey': 'ReleaseEnvironment', 'ParameterValue': release_environment},
                {'ParameterKey': 'Token', 'ParameterValue': get_github_access_token()},
                {'ParameterKey': 'IAMRole', 'ParameterValue': os.environ['IAM_ROLE']}
            ]

            if is_delete_branch_push_event:
                print('Deleting Pipeline Stack')
                # Delete the pipeline stack
                response = delete_stack_if_exists(stack_name)
                print(response)
            else:
                print('Creating or Updating stack')
                print('Attempting to create stack')
                try:
                    create_or_update_stack(
                        create=True, stack_name=stack_name, template_url=template_url,
                        parameters=parameters)
                except Exception as e:
                    print('Stack may have already been created, and that is OK.')
                    print('Error: {0}'.format(e))
                    print('Attempting to update stack')
                    try:
                        create_or_update_stack(
                            create=False, stack_name=stack_name, template_url=template_url,
                            parameters=parameters)
                    except Exception as ex:
                        print('Stack may not need to be updated.')
                        print('Error: {0}'.format(ex))
                        print('Continuing as normal.')

        return {
            "isBase64Encoded" : "false",
            "statusCode": "200",
            "headers": {},
            "body": "Success!"
        }
