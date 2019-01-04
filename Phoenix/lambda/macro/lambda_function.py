"""CloudFormation macro used for additional processing of templates."""
import json
import string
import os
import boto3
import botocore
import tempfile
import copy

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

ssm_client = boto3.client('ssm')
s3_resource = boto3.resource('s3')

PROJECT_NAME = os.environ['PHX_MACRO_PROJECT_NAME']

def safe_print_parameters(list_of_ssm_params):
    ssm_list = copy.deepcopy(list_of_ssm_params)
    for param in ssm_list:
        if param['Type'] == 'SecureString':
            param['Value'] = '*'*len(param['Value'])
    print(json.dumps(ssm_list, indent=2, default=str))

def get_ssm_params_by_path(path):
    """ Returns a list of SSM parameter object.
    [
        {
          "Name": "...",
          "Type": "String",
          "Value": "...",
          "Version": 1,
          "LastModifiedDate": "2018-09-13 14:11:39.928000-07:00",
          "ARN": "..."
        },
        ...
    ]
    """
    result = []
    next_token = ''
    while True:
        args = {
            'Path': path,
            'Recursive': True,
            'WithDecryption': True,
            'MaxResults': 10,
        }
        if next_token:
            args['NextToken'] = next_token
        response = ssm_client.get_parameters_by_path(**args)
        result.extend(response['Parameters'])
        if not response.get('NextToken'):
            break
        next_token = response['NextToken']
    safe_print_parameters(result)
    return result

def get_ssm_map():
    replace_map = {}
    safe_replace_map = {}
    ssm_path = '/microservice/{0}/'.format(PROJECT_NAME)
    ssm_params = get_ssm_params_by_path(ssm_path)
    for param in ssm_params:
        param_key, param_value = param['Name'], param['Value']
        # '/microservice/{project_name}/global/some-param-key' --> 'PHX_MACRO_SOME_PARAM_KEY'
        replace_map[param_key] = param_value
        # Hide the value if this is an encrypted value
        safe_replace_map[param_key] = param_value if param['Type'] != 'SecureString' else '*'*len(param['Value'])
    return replace_map, safe_replace_map

def macro_phoenix_ssm_replace(obj, replace_map, params_map):
    # Replaces dicts of {"PhoenixSSM": /microservice/{ProjectName}/../{Environment}/...}  with SSM values.
    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], dict):
              if "PhoenixSSM" in obj[key]:
                  PhoenixVal = obj[key]["PhoenixSSM"].format(**params_map)
                  replace_val = replace_map.get(PhoenixVal)
                  if replace_val is not None:
                      obj[key] = replace_val
        for key, value in obj.items():
            macro_phoenix_ssm_replace(value, replace_map, params_map)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            if isinstance(item, dict):
                if "PhoenixSSM" in item:
                    PhoenixVal = item["PhoenixSSM"].format(**params_map)
                    replace_val = replace_map.get(PhoenixVal)
                    if replace_val is not None:
                        obj[index] = replace_val
            macro_phoenix_ssm_replace(item, replace_map, params_map)

def get_ssm_project_bucket_name():
    ssm_path = '/microservice/{0}/global/bucket-name'.format(PROJECT_NAME)
    response = ssm_client.get_parameter(
        Name=ssm_path,
        WithDecryption=False
    )
    return response['Parameter']['Value']

def get_obj_from_s3_file(bucketname, filename):
  tmp_file = tempfile.NamedTemporaryFile()
  s3_resource.meta.client.download_file(bucketname, filename, tmp_file.name)
  rfile = open(tmp_file.name, 'r')
  result = json.loads(rfile.read())
  rfile.close()
  return result

def macro_phoenix_s3_transform(obj, params_map, project_bucket_name):
    """Replaces references like the following:

    {"PhoenixS3Transform": "transform-filename.json"}
    {"PhoenixS3Transform": {"Ref": "SomeFilenameParam"}

    ..with JSON from a file in S3.

    It is assume that the file has already been uploaded to the project S3 bucket
    under the 'cloudformation' folder of the bucket.

    This is similar to the CloudFormation Transform AWS::Include macro, but less limiting.
    """
    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], dict):
              if "PhoenixS3Transform" in obj[key]:
                  filename = obj[key]["PhoenixS3Transform"]
                  if isinstance(filename, dict) and "Ref" in filename:
                      # This could be a {"Ref": "filename.json"} reference.
                      filename = params_map[filename["Ref"]]
                  print('filename: ' + filename)
                  obj[key] = get_obj_from_s3_file(s3_bucket, 'cloudformation/{0}'.format(filename))
        for key, value in obj.items():
            macro_phoenix_s3_transform(value, params_map, project_bucket_name)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            if isinstance(item, dict):
                if "PhoenixS3Transform" in item:
                    filename = item["PhoenixS3Transform"]
                    if isinstance(filename, dict) and "Ref" in filename:
                        # This could be a {"Ref": "filename.json"} reference.
                        filename = params_map[filename["Ref"]]
                    print('filename: ' + filename)
                    obj[index] = get_obj_from_s3_file(s3_bucket, 'cloudformation/{0}'.format(filename))
            macro_phoenix_s3_transform(item, params_map, project_bucket_name)

def lambda_handler(event, context):
    print(event)
    print(os.environ)
    print(json.dumps(event, indent=2, default=str))

    fragment = event['fragment']
    replace_map, safe_replace_map = get_ssm_map()
    params_map = event['templateParameterValues']
    params_map.update({'ProjectName': PROJECT_NAME}) # Add the ProjectName to the params map
    print('REPLACE_MAP:', json.dumps(safe_replace_map, indent=2, default=str))

    project_bucket_name = get_ssm_project_bucket_name()

    macro_phoenix_ssm_replace(fragment, replace_map, params_map)
    macro_phoenix_s3_transform(fragment, params_map, project_bucket_name)
    print(json.dumps(fragment, indent=2, default=str))

    return {
        "requestId": event['requestId'],
        "status": "success",
        "fragment": fragment
    }
