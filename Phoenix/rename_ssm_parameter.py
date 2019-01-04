""" Renames SSM parameter keys from an old value to a new value, optionally for encrypted parameters (True|False).

USAGE:
  python rename_ssm_parameter.py {old_param_key} {new_param_key} [True | False]

EXAMPLES:
  python rename_ssm_parameter.py /some/param/key /some/param/new-key True --> param is encrypted.
  python rename_ssm_parameter.py /some/param/key /some/param/new-key False --> param is not encrypted
"""

import sys
import json
import boto3

ssm_client = boto3.client('ssm')

def get_ssm_param(key, with_decryption):
    response = ssm_client.get_parameter(
        Name=key,
        WithDecryption=with_decryption
    )
    return response

def get_most_recent_param(key, with_decryption):
    items = []
    next_token = ''
    while True:
        kwargs = {
            'Name': key,
            'WithDecryption': with_decryption,
            'MaxResults': 5
        }
        if next_token:
            kwargs['NextToken'] = next_token
        response = ssm_client.get_parameter_history(**kwargs)
        items.extend(response.get('Parameters', []))
        next_token = response.get('NextToken')
        if not next_token:
            break
    most_recent_param = sorted(items, key=lambda x: x['Version'], reverse=True)[0]
    tags = ssm_client.list_tags_for_resource(
        ResourceType='Parameter',
        ResourceId=most_recent_param['Name']
    )
    most_recent_param['TagList'] = tags['TagList']
    print('Most recent param:')
    print(most_recent_param)
    return most_recent_param

def create_ssm_param_from_existing_param(old_param, with_encryption, new_key):
    kwargs = {
        'Name': new_key,
        'Type': old_param['Type'],
        'Description': old_param['Description'],
        'Value': old_param['Value'],
        'Overwrite': True
    }
    if with_encryption:
        kwargs['KeyId'] = old_param['KeyId']
    put_response = ssm_client.put_parameter(**kwargs)
    tag_response = ssm_client.add_tags_to_resource(
        ResourceType='Parameter',
        ResourceId=new_key,
        Tags=old_param['TagList']
    )
    return (put_response, tag_response)

def delete_ssm_param(old_param):
    response = ssm_client.delete_parameter(
        Name=old_param['Name']
    )
    return response

def print_json(param):
    print(json.dumps(param, indent=2, default=str))

def main(args):
    if len(args) != 3:
        raise SystemExit('Invalid arguments!')
    old_param_name = args[0]
    new_param_name = args[1]
    encrypt_decrypt = True if args[2] == 'True' else False
    old_param = get_most_recent_param(old_param_name, encrypt_decrypt)
    print_json(old_param)
    create_ssm_param_from_existing_param(old_param, encrypt_decrypt, new_param_name)
    delete_ssm_param(old_param)

if __name__ == '__main__':
    main(sys.argv[1:])
