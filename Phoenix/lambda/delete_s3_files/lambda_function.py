import json
import logging
import uuid
import string
import random
import requests
import boto3
from requests import Request, Session

# This is a CloudFormation Custom Lambda resource that automatically deletes
# all files in one or more S3 buckets. This is particularly useful when deleting S3 bucket
# resources in CloudFormation since CloudFormation cannot delete non-empty S3 buckets.

s3_resource = boto3.resource('s3')

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

def delete_s3_files(bucket_names):
    for bucket_name in bucket_names:
        print('Deleting files in bucket: {}'.format(bucket_name))
        bucket = s3_resource.Bucket(bucket_name)
        bucket.objects.all().delete()

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    response_data = {}
    reason = 'N/A'
    try:
        bucket_names = event['ResourceProperties']['BucketNames']

        if event['RequestType'] == 'Delete':
            delete_s3_files(bucket_names)
        else:
            print('No-Op. This function should only be used on delete stack events.')

        return send_response(event, context, 'SUCCESS', response_data, reason)
    except Exception as e:
        print(e)
        # Change 'FAILED' to 'SUCCESS' for debugging in line below for debugging this Lambda function.
        return send_response(event, context, 'FAILED', response_data, reason)
