import os
import json
import boto3
import botocore
import requests
from datetime import datetime
import urllib.parse

# Handles GitLab merge request events

# For the full GitLab Merge Request REST API:
# https://docs.gitlab.com/ee/api/merge_requests.html

# For the MergeRequest webhook example JSON body:
# https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#merge-request-events

cloudformation_client = boto3.client('cloudformation')
ssm_client = boto3.client('ssm')

class JSONObject:
  def __init__(self, dict):
      vars(self).update(dict)

# Assign python values to values return from gitlab JSON reqeuest object
false = False
true = True
null = None

def get_gitlab_merge_request_notes_url(project_id, merge_request_id, body):
    return (
        '{gitlab_url}/api/v4/projects/{project_id}/'
        'merge_requests/{merge_request_id}/notes?body={body}').format(
            gitlab_url=get_gitlab_url(), project_id=project_id,
            merge_request_id=merge_request_id, body=body)

def get_gitlab_access_token():
    response = ssm_client.get_parameter(
        Name='codebuild-gitlab-access-token',
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_gitlab_url():
    response = ssm_client.get_parameter(
        Name='microservice-gitlab-url',
        WithDecryption=False
    )
    return response['Parameter']['Value']

def get_microservice_bucket_name():
    response = ssm_client.get_parameter(
        Name='microservice-bucket-name',
        WithDecryption=False
    )
    return response['Parameter']['Value']

def notify_gitlab(project_id, merge_request_id, request_body):
    print("Notifying gitlab of start of pipeline")
    request_body = urllib.parse.quote(request_body)
    gitlab_url = get_gitlab_merge_request_notes_url(project_id, merge_request_id, request_body)
    headers = {'Private-Token': get_gitlab_access_token()}
    response = requests.post(gitlab_url, headers=headers)
    print(response)

def lambda_handler(event, context):
    print(event)
    json_obj = json.dumps(event, indent=4)
    print(json_obj)
    obj = json.loads(json_obj, object_hook=JSONObject)
    if obj.object_kind != 'merge_request':
      raise Exception('Object is not a merge request! object is of type' + obj.kind)

    path_with_namespace = obj.project.path_with_namespace               # namespace/reponame
    path_with_namespace_dashes = path_with_namespace.replace('/', '-')  # namespace-reponame
    repo_name = path_with_namespace.split('/')[-1]                      # reponame
    project_id = str(obj.project.id)        # The numeric ID that identifies the GitLab project

    # See https://docs.gitlab.com/ee/api/merge_requests.html
    merge_state = obj.object_attributes.state             # open, closed, merged
    merge_status = obj.object_attributes.merge_status     # can_be_merged, cannot_be_merged, unchecked
    merge_request_internal_id = str(obj.object_attributes.iid) # will be 1 when merge request is initialized.

    source_branch = obj.object_attributes.source_branch.lower()

    stack_name = '{repo_name}-merge-request-{source_branch}-{merge_request_internal_id}'.format(
      repo_name=repo_name,
      source_branch=source_branch.replace('_', '-'),
      merge_request_internal_id=merge_request_internal_id
    )

    template_name = 'template-merge-request-pipeline.json'
    template_url = 'https://s3.amazonaws.com/{0}/cloudformation/{1}'.format(
        get_microservice_bucket_name(), template_name)

    parameters=[
      {
        'ParameterKey': 'PipelineName',
        'ParameterValue': stack_name
      },
      {
        'ParameterKey': 'RepoName',
        'ParameterValue': repo_name
      },
      {
        'ParameterKey': 'GitlabProjectId',
        'ParameterValue': project_id
      },
      {
        'ParameterKey': 'MergeRequestInternalId',
        'ParameterValue': merge_request_internal_id
      },
      {
        'ParameterKey': 'SourceBranch',
        'ParameterValue': obj.object_attributes.source_branch
      }
    ]

    print('merge state is {0}'.format(merge_state))
    print('merge_request_internal_id is {0}'.format(merge_request_internal_id))

    if merge_state in ['merged', 'closed']:
      print('Deleting Pipeline Stack')
      # Delete the pipeline stack
      response = cloudformation_client.delete_stack(
        StackName=stack_name
      )
      print(response)

      print('Deleting ECS Deploy Stack')
      # Delete the ECS deploy stack
      response = cloudformation_client.delete_stack(
        StackName='{0}-{1}-{2}'.format(stack_name, 'ecs', 'deploy')
      )
      print(response)
    else:
      print('Creating or Updating stack')
      print('Attempting to create stack')
      try:
        response = cloudformation_client.create_stack(
          StackName=stack_name,
          TemplateURL=template_url,
          Parameters=parameters,
          Capabilities=['CAPABILITY_IAM']
        )
        # Notify gitlab
        region = os.environ['AWS_DEFAULT_REGION']

        request_body = (
            '<a href="https://console.aws.amazon.com/codepipeline/home?region='
            '{region}#/view/{pipeline_name}">View Pipeline</a> &nbsp; &nbsp; '
            ' {emoji} ').format(
                region=region, pipeline_name=stack_name,
                emoji=MONTH_EMOJI_MAP.get(datetime.now().month, ':white_check_mark:'))
        notify_gitlab(project_id, merge_request_internal_id, request_body)
      except Exception as e:
        print('Stack may have already been created, and that is OK.')
        print('Error: {0}'.format(e))
        print('Continuing as normal. There is no need to update the stack once it is deleted')


MONTH_EMOJI_MAP = {
    10: ':jack_o_lantern: :white_check_mark: :ghost:',
    12: ':christmas_tree: :white_check_mark: :gift:'
}
