import os
import json
import boto3
import botocore
import random
import string
import requests
from datetime import datetime
import urllib.parse
import uuid
import hmac

# Creates a secret in SSM parameter store

ssm_client = boto3.client('ssm')

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

def get_random_secret(secret_length=20):
    password = ''
    char_set = string.ascii_uppercase + string.ascii_lowercase + string.digits + '$'
    while '$' not in password:
        password = ''.join(random.sample(char_set * 6, int(secret_length)))
    return password

def put_ssm_secret(kwargs):
    print('putting SSM secret')
    kwargs['Value'] = get_random_secret(kwargs['SecretLength'])
    del kwargs['SecretLength']
    kwargs['Type'] = 'SecureString'
    response = ssm_client.put_parameter(**kwargs)

def delete_ssm_secret(kwargs):
    print('deleting SSM secret')
    new_kwargs = {'Name': kwargs['Name']}
    response = ssm_client.delete_parameter(**new_kwargs)
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
        kwargs = event['ResourceProperties']['SSMSecret']
        replace_map = {"true": True, "false": False}
        clean_params(kwargs, replace_map)
        if event['RequestType'] == 'Create':
            put_ssm_secret(kwargs)
        elif event['RequestType'] == 'Update':
            put_ssm_secret(kwargs)
        elif event['RequestType'] == 'Delete':
            delete_ssm_secret(kwargs)
        else:
            print('No-Op. This function should only be used on create, update, and delete stack events.')
    except Exception as e:
        print(e)
        # Change 'FAILED' to 'SUCCESS' for debugging in line below for debugging this Lambda function.
        return send_response(event, context, 'FAILED', response_data, reason)

    return send_response(event, context, 'SUCCESS', response_data, reason)
