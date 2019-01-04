import os
import json
import boto3
import botocore
import requests
from datetime import datetime
import urllib.parse
import uuid
import hmac

# Creates a GitHub webhook within GitHub for sending pull request webhooks

# For the full GitHub Pull Request REST API:
# https://developer.github.com/v3/activity/events/types/#pullrequestevent

cloudformation_client = boto3.client('cloudformation')
ssm_client = boto3.client('ssm')

GITHUB_API_URL = 'https://api.github.com'

def send_response(event, context, response_status, response_data, reason):
    """Send a Success or Failure event back to CFN stack"""

    payload = {
        'StackId': event['StackId'],
        'Status' : response_status,
        'Reason' : reason,
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }

    payload['PhysicalResourceId'] = event.get(
        'PhysicalResourceId', str(uuid.uuid4()))

    print("Sending %s to %s" % (json.dumps(payload, default=str, indent=2), event['ResponseURL']))
    requests.put(event['ResponseURL'], data=json.dumps(payload, default=str))
    print("Sent %s to %s" % (json.dumps(payload, default=str, indent=2), event['ResponseURL']))

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

def create_webhook(kwargs, repo_name):
    url = os.path.join(GITHUB_API_URL, 'repos/{0}/{1}/hooks'.format(
        os.environ['GITHUB_ORGANIZATION'], repo_name))
    # Create a secret token and save to SSM parameter store
    access_token = get_github_access_token()
    headers = {'Authorization': 'token {0}'.format(access_token)}
    secret = get_github_pull_request_secret() # Gets the secret from SSM parameter store
    webhook_url = kwargs['config']['url']
    kwargs['name'] = 'web' # This must always be 'web' for webhooks.
    kwargs['config'] = {
        'url': webhook_url,
        'content_type': 'json',
        'secret': secret
    }
    response = requests.post(url, data=json.dumps(kwargs), headers=headers)
    print(json.dumps(response.json(), indent=2))

def update_webhook(kwargs, repo_name):
    # Deletes all webhooks associated with a given name
    webhook_api_url = 'repos/{0}/{1}/hooks'.format(
        os.environ['GITHUB_ORGANIZATION'], repo_name)
    list_url = os.path.join(GITHUB_API_URL, webhook_api_url)
    access_token = get_github_access_token()
    headers = {'Authorization': 'token {0}'.format(access_token)}
    response = requests.get(list_url, headers=headers)
    print(json.dumps(json.loads(response.text), indent=2, default=str))
    response_obj = json.loads(response.text)
    for webhook in response_obj:
        print('webook: ', webhook)
        if webhook['config']['url'] == kwargs['config']['url']:
            secret = get_github_pull_request_secret() # Gets the secret from SSM parameter store
            kwargs['config'] = {
                'url': kwargs['config']['url'],
                'content_type': 'json',
                'secret': secret
            }
            update_url = os.path.join(GITHUB_API_URL, webhook_api_url, str(webhook['id']))
            print('Updating webhook {0} with id {1}'.format(webhook['config']['url'], webhook['id']))
            response = requests.patch(update_url, data=json.dumps(kwargs), headers=headers)
            print(json.dumps(response.json(), indent=2))

def delete_webhook(webhook_url, repo_name):
    # Deletes all webhooks associated with a given name
    webhook_api_url = 'repos/{0}/{1}/hooks'.format(
        os.environ['GITHUB_ORGANIZATION'], repo_name)
    list_url = os.path.join(GITHUB_API_URL, webhook_api_url)
    access_token = get_github_access_token()
    headers = {'Authorization': 'token {0}'.format(access_token)}
    response = requests.get(list_url, headers=headers)
    print(json.dumps(json.loads(response.text), indent=2, default=str))
    response_obj = json.loads(response.text)
    for webhook in response_obj:
        print('webook: ', webhook)
        if webhook['config']['url'] == webhook_url:
            delete_url = os.path.join(GITHUB_API_URL, webhook_api_url, str(webhook['id']))
            print('Deleting webhook {0} with id {1}'.format(webhook['config']['url'], webhook['id']))
            response = requests.delete(delete_url, headers=headers)
            print(response)

def clean_params(obj, replace_map):
    # Recursive function to set all values to Python types.
    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], str):
                if obj[key] in replace_map:
                    obj[key] = replace_map.get(obj[key])
                    continue
                try:
                    new_val = int(obj[key])
                    obj[key] = new_val
                except Exception:
                    continue
        for key, value in obj.items():
            clean_params(value, replace_map)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            if isinstance(item, str):
                if obj[index] in replace_map:
                    obj[index] = replace_map.get(obj[index])
                    continue
                try:
                    new_val = int(obj[index])
                    obj[index] = new_val
                except Exception:
                    continue
            clean_params(item, replace_map)

def lambda_handler(event, context):
    response_data = {}
    reason = 'N/A'
    try:
        print(json.dumps(event, indent=2))
        # For the structure of kwargs, see the following:
        #   https://developer.github.com/v3/repos/hooks/#create-a-hook
        #   DO NOT provide the secret, as it will be generated by this Lambda function.
        kwargs = event['ResourceProperties']['GitHubWebhookParams']
        # Name of the repository on which to attach the webhook
        repo_name = event['ResourceProperties']['RepoName']
        replace_map = {"true": True, "false": False}
        clean_params(kwargs, replace_map)
        if event['RequestType'] == 'Create':
            create_webhook(kwargs, repo_name)
        elif event['RequestType'] == 'Update':
            update_webhook(kwargs, repo_name)
        elif event['RequestType'] == 'Delete':
            delete_webhook(kwargs['config']['url'], repo_name)
        else:
            print('No-Op. This function should only be used on create, update, and delete stack events.')
    except Exception as e:
        print(e)
        # Change 'FAILED' to 'SUCCESS' for debugging in line below for debugging this Lambda function.
        return send_response(event, context, 'FAILED', response_data, reason)

    return send_response(event, context, 'SUCCESS', response_data, reason)
