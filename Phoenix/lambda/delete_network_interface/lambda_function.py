import json
import logging
import uuid
import string
import random
import requests
import boto3
from requests import Request, Session

# This function force deletes the ENI associated with a Lambda function residing
# inside of a VPC. There is currently a bug in CloudFormation not deleting lambda
# functions created inside of a VPC upon stack deletion.
# https://forums.aws.amazon.com/thread.jspa?messageID=756642
# TODO (jason.debolt): Delete this function once AWS figures out how to automatically
# delete these interfaces.

ec2_client = boto3.client('ec2')

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


def delete_network_interface(security_group_id):
    eni = ec2_client.describe_network_interfaces(Filters=[{
        'Name': 'group-id',
        'Values': [security_group_id]
    }])
    if len(eni.get('NetworkInterfaces', [])) > 0:
        print(json.dumps(eni, default=str, indent=2))
        network_interface = eni.get('NetworkInterfaces', [{}])[0]
        if network_interface:
            network_interface_id = network_interface.get('NetworkInterfaceId')
            print('network_interface_id: {0}'.format(network_interface_id))

            # A NetworkInterfaces must be detached before it can be deleted.
            print('Checking if the networking interface is currently attached')
            attachment = network_interface.get('Attachment', {})
            if attachment and 'AttachmentId' in attachment:
                attachment_id = attachment['AttachmentId']
                print('network interface has an attachment id {0}'.format(attachment_id))
                print('attempting to detach network interface')
                detachment_response = ec2_client.detach_network_interface(
                    AttachmentId=attachment_id,
                    Force=True)
                print(detachment_response)
            else:
                print('No attachment or AttachmentId found in network interface. Skipping detachment.')

            print('attempting to delete network interface')
            delete_response = ec2_client.delete_network_interface(
                NetworkInterfaceId=network_interface_id
            )
            print(delete_response)
    else:
        print('There are not network interfaces associated with '
              'security group {0}'.format(security_group_id))

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    response_data = {}
    security_group_id = event['ResourceProperties']['SecurityGroupId']
    reason = 'N/A'

    if event['RequestType'] == 'Delete':
        delete_network_interface(security_group_id)
    else:
        print('No-Op. This function should only be used on delete stack events.')

    return send_response(event, context, 'SUCCESS', response_data, reason)
