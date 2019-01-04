import os
import json
import boto3
import botocore
import requests
from datetime import datetime
import urllib.parse
import hmac
import base64

# Handles GitHub pull request events

# For the full GitHub Pull Request REST API:
# https://developer.github.com/v3/activity/events/types/#pullrequestevent

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

def get_github_pull_request_secret():
    print('getting github pull request secret')
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/github/pull-request-secret'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_microservice_bucket_name():
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/bucket-name'.format(os.environ['PROJECT_NAME']),
        WithDecryption=False
    )
    return response['Parameter']['Value']

def notify_github(pull_request_number, request_body):
    url = os.path.join(GITHUB_API_URL, 'repos/{0}/{1}/issues/{2}/comments'.format(
        os.environ['GITHUB_ORGANIZATION'], os.environ['PROJECT_NAME'], pull_request_number))
    payload = { "body": request_body }
    headers = {'Authorization': 'token {0}'.format(get_github_access_token())}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(json.dumps(response.json(), indent=2))

def create_or_update_stack(
    create, stack_name, template_url, parameters, pull_request_number):
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
    # Notify gitlab
    region = os.environ['AWS_DEFAULT_REGION']

    # GitHub markdown can be found here
    #   https://gist.github.com/rxaviers/7360908
    request_body = (
        '<a href="https://console.aws.amazon.com/codepipeline/home?region='
        '{region}#/view/{pipeline_name}">View Pipeline</a> &nbsp; &nbsp; '
        ' {emoji} ').format(
            region=region, pipeline_name=stack_name,
            emoji=MONTH_EMOJI_MAP.get(datetime.now().month, ':white_check_mark:'))
    notify_github(pull_request_number, request_body)

def lambda_handler(event, context):
    print(event)

    # I used Lambda proxy integration here.
    github_signature = event['headers']['X-Hub-Signature']
    secret = get_github_pull_request_secret()
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
        # For a full list of events: https://developer.github.com/v3/activity/events/types/#pullrequestevent
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

        if not hasattr(body, 'pull_request'):
            raise Exception('Object is not a pull request!')

        repo_name = body.pull_request.head.repo.name # reponame
        source_branch = body.pull_request.head.ref # The pull request branch name
        pull_request_number = str(body.pull_request.number) # Unique ID for the pull request within this repo.

        stack_name = '{repo_name}-pull-request-{source_branch}-{pull_request_number}'.format(
            repo_name=repo_name,
            source_branch=source_branch.replace('_', '-'),
            pull_request_number=pull_request_number
        )
        print('stack_name: ', stack_name)

        template_name = 'template-pull-request-pipeline.json'
        template_url = 'https://s3.amazonaws.com/{0}/cloudformation/{1}'.format(
            get_microservice_bucket_name(), template_name)

        print('template_url: ', template_url)

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
            {'ParameterKey': 'PullRequestNumber', 'ParameterValue': pull_request_number},
            {'ParameterKey': 'SourceBranch', 'ParameterValue': source_branch},
            {'ParameterKey': 'Token', 'ParameterValue': get_github_access_token()},
            {'ParameterKey': 'IAMRole', 'ParameterValue': os.environ['IAM_ROLE']}
        ]
        print('Parameters: ', parameters)

        pull_request_state = body.pull_request.state

        if pull_request_state == "closed":
            print('Deleting Pipeline Stack')
            # Delete the pipeline stack
            response = cloudformation_client.delete_stack(
              StackName=stack_name
            )
            print(response)

            print('Deleting ECS Main Deploy Stack')
            # Delete the ECS MAIN Task deploy stack
            main_deploy_stack_name = '{0}-{1}-{2}-{3}'.format(stack_name, 'ecs', 'main', 'deploy')
            print(main_deploy_stack_name)
            response = cloudformation_client.delete_stack(
              StackName=main_deploy_stack_name
            )
            print(response)

            print('Waiting on ECS Main Deploy Stack deletion...')
            main_deploy_waiter = cloudformation_client.get_waiter('stack_delete_complete')
            main_deploy_waiter.wait(StackName=main_deploy_stack_name)

            print('Deleting EC2 Deploy Stack')
            # Delete the EC2 deploy stack
            response = cloudformation_client.delete_stack(
              StackName='{0}-{1}-{2}'.format(stack_name, 'ec2', 'deploy')
            )
            print(response)

            print('Deleting Lambda Stack')
            # Delete the EC2 deploy stack
            response = cloudformation_client.delete_stack(
              StackName='{0}-{1}-{2}'.format(stack_name, 'lambda', 'deploy')
            )
            print(response)

            print('Deleting SSM Environments Parameter Stack')
            # Delete the EC2 deploy stack
            response = cloudformation_client.delete_stack(
              StackName='{0}-{1}-{2}'.format(stack_name, 'ssm-environments', 'deploy')
            )
            print(response)
        elif pull_request_state == "open":
            print('Creating or Updating stack')
            print('Attempting to create stack')
            try:
                create_or_update_stack(
                    create=True, stack_name=stack_name, template_url=template_url,
                    parameters=parameters, pull_request_number=pull_request_number)
            except Exception as e:
                print('Stack may have already been created, and that is OK.')
                print('Error: {0}'.format(e))
                print('Attempting to update stack')
                try:
                  create_or_update_stack(
                      create=False, stack_name=stack_name, template_url=template_url,
                      parameters=parameters, pull_request_number=pull_request_number)
                except Exception as ex:
                    print('Stack may not need to be updated.')
                    print('Error: {0}'.format(ex))
                    print('Continuing as normal. There is no need to update the stack once it is deleted')
        else:
            print('Unknown pull request state: ', pull_request_state)

        return {
            "isBase64Encoded" : "false",
            "statusCode": "200",
            "headers": {},
            "body": "Success!"
        }


MONTH_EMOJI_MAP = {
    10: ':jack_o_lantern: :white_check_mark: :ghost:',
    12: ':christmas_tree: :white_check_mark: :gift:'
}
