import json
import boto3
import botocore

# Handles GitLab merge request events

# For the full GitLab Merge Request REST API:
# https://docs.gitlab.com/ee/api/merge_requests.html

# For the MergeRequest webhook example JSON body:
# https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#merge-request-events

cloudformation_client = boto3.client('cloudformation')

class JSONObject:
  def __init__(self, dict):
      vars(self).update(dict)

# Assign python values to values return from gitlab JSON reqeuest object
false = False
true = True
null = None

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
    project_id = obj.project.id        # The numeric ID that identifies the GitLab project

    # See https://docs.gitlab.com/ee/api/merge_requests.html
    merge_state = obj.object_attributes.state             # open, closed, merged
    merge_status = obj.object_attributes.merge_status     # can_be_merged, cannot_be_merged, unchecked
    merge_request_internal_id = obj.object_attributes.iid # will be 1 when merge request is initialized.

    source_branch = obj.object_attributes.source_branch.lower()

    stack_name = '{repo_name}-{source_branch}-{merge_request_internal_id}'.format(
      repo_name=repo_name,
      source_branch=source_branch,
      merge_request_internal_id=merge_request_internal_id
    )

    bucket_name = 'mosaic-phoenix-microservice'
    template_name = 'template-merge-request-pipeline.json'
    template_url = 'https://s3.amazonaws.com/{0}/cloudformation/{1}'.format(bucket_name, template_name)

    parameters=[
      {
        'ParameterKey': 'ProjectName',
        'ParameterValue': repo_name
      },
      {
        'ParameterKey': 'PipelineName',
        'ParameterValue': stack_name
      },
      {
        'ParameterKey': 'RepoName',
        'ParameterValue': repo_name
      },
      {
        'ParameterKey': 'SourceBranch',
        'ParameterValue': obj.object_attributes.source_branch
      }
    ]

    print('merge state is {0}'.format(merge_state))
    print('merge_request_internal_id is {0}'.format(merge_request_internal_id))

    if merge_state in ['merged', 'closed']:
      print('Deleting Stack')
      response = cloudformation_client.delete_stack(
        StackName=stack_name
      )
      print('response')
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
        print('response')
      except Exception as e:
        print('Stack may have already been created, and that is OK.')
        print('Error: {0}'.format(e))
        print('Continuing as normal. There is no need to update the stack once it is deleted')
