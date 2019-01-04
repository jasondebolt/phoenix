""" A CloudFormation custom resource for creating ALB redirection rules.

This is particularly useful for adding HTTP->HTTPS redirects to Application
Load Balancers.

At the time this was created, AWS had introduced redirect rules on ALBs but
had not yet made them available in CloudFormation. The boto3 Python library
does support it however.

Original Git Repo:
https://github.com/jheller/alb-rule/blob/master/lambda/alb_listener_rule.py
"""

import boto3
from botocore.exceptions import ClientError, ParamValidationError
import sys
import os
import json
import requests
from requests import Request, Session


def send_response(event, context, response_status, response_data):
    """Send a Success or Failure event back to CFN stack"""

    print('response_status: ' + response_status)
    print('response_data: ' + json.dumps(response_data))

    payload = {
        'StackId': event['StackId'],
        'Status' : response_status,
        'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
        'PhysicalResourceId': context.log_stream_name,
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }

    print('Sending %s to %s' % (json.dumps(payload), event['ResponseURL']))
    requests.put(event['ResponseURL'], data=json.dumps(payload))
    print('Sent %s to %s' % (json.dumps(payload), event['ResponseURL']))


def lambda_handler(event, context):
    try:
        print('Lambda Event: ' + json.dumps(event))

        response_data = {}

        region = os.environ['AWS_REGION']
        event_type = event['RequestType']

        listener_arn = event['ResourceProperties']['ListenerArn']
        conditions = event['ResourceProperties']['Conditions']
        actions = event['ResourceProperties']['Actions']
        priority = int(event['ResourceProperties']['Priority'])

        alb = boto3.client('elbv2')

        if event_type == 'Create':
            create_rule(alb, listener_arn, conditions, priority, actions)
            response_status = 'SUCCESS'

        elif event_type == 'Delete':
            delete_rule(alb, listener_arn, priority)
            response_status = 'SUCCESS'

        elif event_type == 'Update':
            old_priority = int(event['OldResourceProperties']['Priority'])
            delete_rule(alb, listener_arn, old_priority)
            create_rule(alb, listener_arn, conditions, priority, actions)
            response_status = 'SUCCESS'

    except ClientError as e:
        print('Boto ClientError: {0}'.format(e))
        response_status = 'FAILED'
    except ParamValidationError as e:
        print('Boto ParamValidationError: {0}'.format(e))
        response_status = 'FAILED'
    except TypeError as e:
        print('TypeError: {0}'.format(e))
        response_status = 'FAILED'
    except NameError as e:
        print('NameError: {0}'.format(e))
        response_status = 'FAILED'
    except AttributeError as e:
        print('AttributeError: {0}'.format(e))
        response_status = 'FAILED'
    except:
        print('Error:', sys.exc_info()[0])
        response_status = 'FAILED'

    return send_response(event, context, response_status, response_data)

def create_rule(alb, listener_arn, conditions, priority, actions):
    print('create_rule ' + listener_arn)
    response = alb.create_rule(
        ListenerArn=listener_arn,
        Conditions=conditions,
        Priority=priority,
        Actions=actions
    )

def delete_rule(alb, listener_arn, priority):
    print('delete_rule with priority: %d' % priority)
    response = alb.describe_rules(ListenerArn=listener_arn)
    print('Found rules: ' + json.dumps(response))
    for rule in response['Rules']:
        if rule['IsDefault']:
            continue
        if int(rule['Priority']) == priority:
            RuleArn = rule['RuleArn']
            print('Deleting rule: ' + json.dumps(rule))
            response=alb.delete_rule(RuleArn=RuleArn)
            break
