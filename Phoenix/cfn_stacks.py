""" Helper script used to work with CloudFormation stacks.

USAGE:
  python cfn_stacks.py delete-if-exists {stack_name}
  python cfn_stacks.py disable-termination-protection {stack_name}

 EXAMPLES:
  python cfn_stacks.py delete-if-exists some-stack-name
  python cfn_stacks.py disable-termination-protection some-stack-name
"""

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

import sys
import json
import boto3
import botocore

cloudformation_client = boto3.client('cloudformation')


def delete_if_exists(stack_name):
    # Idempotent way to delete a CloudFormation stack.
    try:
      print('Attempting to delete stack {0}'.format(stack_name))
      response = cloudformation_client.delete_stack(
        StackName=stack_name)
      print(json.dumps(response, indent=2, default=str))
    except Exception as e:
      print('Error: {0}'.format(e))
      print('Stack {0} may not exist. Skipping delete.'.format(stack_name))


def disable_termination_protection(stack_name):
    # Idempotent way to disable termination protection on a CloudFormation stack.
    try:
      print('Attempting to disable termination protection on stack {0}'.format(stack_name))
      response = cloudformation_client.update_termination_protection(
          EnableTerminationProtection=False,
          StackName=stack_name)
      print(json.dumps(response, indent=2, default=str))
    except Exception as e:
      print('Error: {0}'.format(e))
      print('Stack {0} may not already exist. Skipping delete.'.format(stack_name))


def main(args):
    if len(args) != 2:
        raise SystemExit('Invalid arguments!')
    command_name = args[0]
    stack_name = args[1]
    if command_name == 'delete-if-exists':
        delete_if_exists(stack_name)
    elif command_name == 'disable-termination-protection':
        disable_termination_protection(stack_name)

if __name__ == '__main__':
    main(sys.argv[1:])
