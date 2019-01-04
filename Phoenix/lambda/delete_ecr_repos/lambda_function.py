import json
import logging
import uuid
import string
import random
import requests
import boto3
from requests import Request, Session

# This is a CloudFormation Custom Lambda resource that automatically deletes
# all images in one or more ECR repos, as well as the ECR repo itself. This is
# particularly useful when deleting ECR repos in CloudFormation since
# CloudFormation cannot delete non-empty ECR repos.

ecr_client = boto3.client('ecr')

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

    print("Sending %s to %s" % (json.dumps(payload), event['ResponseURL']))
    requests.put(event['ResponseURL'], data=json.dumps(payload))
    print("Sent %s to %s" % (json.dumps(payload), event['ResponseURL']))

def delete_ecr_repos(ecr_repo_names):
    for repo_name in ecr_repo_names:
        print('Deleting ecr repo: {}'.format(repo_name))
        response = ecr_client.delete_repository(
            repositoryName=repo_name,
            force=True
        )

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    response_data = {}
    reason = 'N/A'
    try:
        ecr_repo_names = event['ResourceProperties']['ECRRepoNames']

        if event['RequestType'] == 'Delete':
            delete_ecr_repos(ecr_repo_names)
        else:
            print('No-Op. This function should only be used on delete stack events.')

        return send_response(event, context, 'SUCCESS', response_data, reason)
    except Exception as e:
        print(e)
        # Change 'FAILED' to 'SUCCESS' for debugging in line below for debugging this Lambda function.
        return send_response(event, context, 'FAILED', response_data, reason)
