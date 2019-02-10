"""Generates, encrypts, and stores RDS instance MasterUser passwords in SSM parameter store.

Also retrieves said passwords and returns to a Cloudformation stack.

Please make sure to perform the following testing plan when making changes to this Lambda function:

https://docs.google.com/document/d/16UUY3h-4wU372XF8D0Fs1IQ3ABLrO-Vjn5ao2YkB84M/edit#heading=h.ww33z0t9wm7h
"""
import json
import logging
import uuid
import string
import random
import requests
import boto3
import copy
from requests import Request, Session

ssm_client = boto3.client('ssm')
secretsmanager_client = boto3.client('secretsmanager')

def put_password_to_ssm(parameter_name, parameter_description, key_id, password):
    """Puts the password to SSM Parameter Store."""
    print('Putting password to parameter store')
    kwargs = {
        'Name': parameter_name,
        'Description': parameter_description,
        'Value': password,
        'Type': 'SecureString',
        'Overwrite': True
    }
    if key_id is not None:
        kwargs['KeyId'] = key_id
    response = ssm_client.put_parameter(**kwargs)
    return response

def get_password_from_ssm(parameter_name, key_id):
    """Retrieves the password from SSM Parameter Store."""
    response = ssm_client.get_parameters(
        Names=[parameter_name], WithDecryption=True)
    credentials = response['Parameters'][0]['Value']
    return credentials

def get_random_password(password_length=20):
    password = ''
    char_set = string.ascii_uppercase + string.ascii_lowercase + string.digits + '$'
    while '$' not in password:
        password = ''.join(random.sample(char_set * 6, int(password_length)))
    return password

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

    safe_payload = copy.deepcopy(payload)
    if 'Password' in safe_payload['Data']:
        del safe_payload['Data']['Password'] # Don't display password in logs

    print("Sending %s to %s" % (json.dumps(safe_payload), event['ResponseURL']))
    requests.put(event['ResponseURL'], data=json.dumps(payload))

    print("Sent %s to %s" % (json.dumps(safe_payload), event['ResponseURL']))


def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    response_data = {}
    kms_key_id = event['ResourceProperties']['KMSKeyId']
    param_name = event['ResourceProperties']['ParameterName']
    param_description = event['ResourceProperties']['ParameterDescription']
    password_length = int(event['ResourceProperties']['PasswordLength'])
    snapshot_identifier = event['ResourceProperties'].get('SnapshotIdentifier', "")
    reason = 'N/A'

    if event['RequestType'] == 'Create':
        if event['ResourceProperties']['Type'] == 'encrypt':
            # DB is created either brand new/empty or from a snapshot.
            # If from snapshot, no new password is generated or persisted to SSM parameter store.
            # The ONLY case where we want to generate and store a password is upon stack creation of brand new RDS instance (empty snapshot ID).
            if snapshot_identifier == "":
                db_password = get_random_password(password_length)
                put_password_to_ssm(param_name, param_description, kms_key_id, db_password)
                reason = 'The value was successfully encrypted'
        elif event['ResourceProperties']['Type'] == 'decrypt':
            # Return the decrypted password to any stack that wants it and has the correct
            # permissions to decrypt for a stack create operation.
            # If this is a create+decrypt operation from a new RDS instance, the returned value will be used in the MasterUserName
            # If this is a create+decrypt operation from a snapshot restored RDS instance, the returned password will be RDS Cluster resource.
            response_data['Password'] = get_password_from_ssm(param_name, kms_key_id)
            reason = 'The value was successfully decrypted'
    elif event['RequestType'] == 'Update':
        # The MasterUserPassword cannot be updated in Cloudformation templates, so the returned values gets ignored by the AWS::RDS::DBCluster resource in all cases.
        # If this is an update+decrypt operation from another client, it will do whatever it wants with the returned value.
        if event['ResourceProperties']['Type'] == 'decrypt':
            response_data['Password'] = get_password_from_ssm(param_name, kms_key_id)
            reason = 'The value was successfully decrypted'
    elif event['RequestType'] == 'Delete':
        print('Delete stack operation, Lambda NoOp.')

    return send_response(event, context, 'SUCCESS', response_data, reason)
