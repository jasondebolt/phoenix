""" Make various Cognito API and Route53 calls to further configure Cognito User Pools."""
import json
import logging
import uuid
import string
import random
import requests
import boto3
import botocore
from requests import Request, Session

cognito_client = boto3.client('cognito-idp')
route53_client = boto3.client('route53')

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


def change_resource_record_set(hosted_zone_id, alias_target_hosted_zone_id, record_set_dns_name, record_set_name, action):
    print('Attempting to {0} auth record set'.format(action))
    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': 'Cognito auth domain for Cognito user pools.',
                'Changes': [
                    {
                        'Action': action,
                        'ResourceRecordSet': {
                            'Name': record_set_name,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': alias_target_hosted_zone_id,
                                'DNSName': record_set_dns_name,
                                'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )
    except Exception as e:
        print(e)
        print('Auth record set {0} operation failed. Record set may already have been created or deleted by a previous stack. This is expected.'.format(action))


def create_user_pool_domain(domain, user_pool_id):
    try:
        response = cognito_client.create_user_pool_domain(
            Domain=domain,
            UserPoolId=user_pool_id
        )
        print(response)
    except Exception as e:
        # If the user pool domain was previously created, let's return the cloudfront alias associated with the current domain.
        print(e)
        print('Unable to create non-custom user pool domain. This may have been already previously created.')


def create_user_pool_custom_domain(custom_domain, user_pool_id, auth_ssl_certificate_arn):
    try:
        response = cognito_client.create_user_pool_domain(
            Domain=custom_domain,
            UserPoolId=user_pool_id,
            CustomDomainConfig={
                'CertificateArn': auth_ssl_certificate_arn
            }
        )
        print(response)
        return response['CloudFrontDomain']
    except Exception as e:
        # If the user pool domain was previously created, let's return the cloudfront alias associated with the current domain.
        print(e)
        print('create user pool custom domain failed')
        print('attempting to get existing user pool custom domain')
        try:
            response = cognito_client.describe_user_pool_domain(Domain=custom_domain)
            print(response)
            return response['DomainDescription']['CloudFrontDistribution']
        except Exception as e:
            print(e)
            print('describe user pool domain failed, could not describe user pool domain')


def update_user_pool_client(user_pool_id, client_id, resource_server_scope):
    response = cognito_client.update_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        ExplicitAuthFlows=['ADMIN_NO_SRP_AUTH'],
        AllowedOAuthFlows=['client_credentials'],
        AllowedOAuthScopes=[resource_server_scope]
    )
    print(response)


def delete_user_pool_domain(custom_domain, user_pool_id):
    try:
        response = cognito_client.delete_user_pool_domain(
            Domain=custom_domain,
            UserPoolId=user_pool_id
        )
        print(response)
    except Exception as e:
        print(e)
        print('delete_user_pool_domain failed. Continue as normal as this CloudFormation distribution may already exist.')
        try:
            print('Attempting to return name of existing cloudfront distribution.')
            domain_obj = cognito_client.describe_user_pool_domain(Domain=custom_domain)
            return domain_obj['DomainDescription']['CloudFrontDistribution']
        except Exception as ex:
            print(e)
            print('failed to describe existing cloudfront distribution.')


def create_resource_server(user_pool_id, client_id, resource_server_identifier,
                           resource_server_name, resource_server_scope):
    response = cognito_client.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier=resource_server_identifier,
        Name=resource_server_name,
        Scopes=[
            {
                'ScopeName': resource_server_scope,
                'ScopeDescription': resource_server_scope
            }
        ]
    )
    print(response)

def update_resource_server(user_pool_id, client_id, resource_server_identifier,
                           resource_server_name, resource_server_scope):
    response = cognito_client.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier=resource_server_identifier,
        Name=resource_server_name,
        Scopes=[
            {
                'ScopeName': resource_server_scope,
                'ScopeDescription': resource_server_scope
            }
        ]
    )
    print(response)

def delete_resource_server(user_pool_id, resource_server_identifier):
    response = client.delete_resource_server(
        UserPoolId=user_pool_id,
        Identifier=resource_server_identifier
    )
    print(response)

def lambda_handler(event, context):
    response_data = {}
    reason = 'N/A'
    try:
        print(json.dumps(event, indent=2))
        cognito_domain = event['ResourceProperties']['CognitoDomain'] # {project-name}-{environment}
        api_domain = event['ResourceProperties']['APIDomain']  # api.mosaic-credit.com
        auth_domain = event['ResourceProperties']['AuthDomain']  # auth.api.mosaic-credit.com
        custom_domain = event['ResourceProperties']['CustomDomain'] # {environment}.auth.api.mosaic-credit.com
        domain_prefix = event['ResourceProperties']['DomainPrefix'] # {prefix}-{environment}
        use_custom_domain = event['ResourceProperties']['UseCustomDomain'] == "true" # AWS accounts have a hard limit of 4 custom domains.
        hosted_zone_id = event['ResourceProperties']['HostedZoneId']
        cloudfront_hosted_zone_id = 'Z2FDTNDATAQYW2' # htps://docs.aws.amazon.com/general/latest/gr/rande.html
        user_pool_id = event['ResourceProperties']['UserPoolId']
        client_id = event['ResourceProperties']['ClientId']
        cognito_ssl = event['ResourceProperties']['ClientId']
        resource_server_identifier = event['ResourceProperties']['ResourceServerIdentifier']
        resource_server_name = event['ResourceProperties']['ResourceServerName']
        resource_server_scope = event['ResourceProperties']['ResourceServerScope']
        auth_ssl_certificate_arn = event['ResourceProperties']['AuthSSLCertificateARN']

        if event['RequestType'] == 'Create':
            # This is an account-wide route53 record set. The auth_domain should be created once for the entire account.
            # If this route53 record set was already created, an exception is caught and logged so that Lambda execution does not fail.
            change_resource_record_set( # Creates the auth route53 record set (auth.api.mosaic-credit.com)
                hosted_zone_id=hosted_zone_id, alias_target_hosted_zone_id=hosted_zone_id,
                record_set_dns_name=api_domain, record_set_name=auth_domain, action='CREATE')
            create_user_pool_domain(domain=domain_prefix, user_pool_id=user_pool_id)
            if use_custom_domain:
                cloudfront_domain = create_user_pool_custom_domain(
                    custom_domain=custom_domain, user_pool_id=user_pool_id,
                    auth_ssl_certificate_arn=auth_ssl_certificate_arn)
                change_resource_record_set( # Creates the auth route53 record set ({environment}.auth.api-mosaic-credit.com)
                    hosted_zone_id=hosted_zone_id, alias_target_hosted_zone_id=cloudfront_hosted_zone_id,
                    record_set_dns_name=cloudfront_domain, record_set_name=custom_domain, action='CREATE')
            create_resource_server(
                user_pool_id=user_pool_id, client_id=client_id,
                resource_server_identifier=resource_server_identifier,
                resource_server_name=resource_server_name,
                resource_server_scope=resource_server_scope)
            update_user_pool_client( # This resource is already created in CloudFormation.
                user_pool_id=user_pool_id,
                client_id=client_id,
                resource_server_scope='{0}/{1}'.format(resource_server_identifier, resource_server_scope))
        elif event['RequestType'] == 'Update':
            create_user_pool_domain(domain=domain_prefix, user_pool_id=user_pool_id)
            if use_custom_domain:
                cloudfront_domain = create_user_pool_custom_domain(
                    custom_domain=custom_domain, user_pool_id=user_pool_id,
                    auth_ssl_certificate_arn=auth_ssl_certificate_arn)
                change_resource_record_set( # Creates the auth route53 record set ({environment}.auth.api-mosaic-credit.com)
                    hosted_zone_id=hosted_zone_id, alias_target_hosted_zone_id=cloudfront_hosted_zone_id,
                    record_set_dns_name=cloudfront_domain, record_set_name=custom_domain, action='UPSERT')
            update_resource_server(
                user_pool_id=user_pool_id, client_id=client_id,
                resource_server_identifier=resource_server_identifier,
                resource_server_name=resource_server_name,
                resource_server_scope=resource_server_scope)
        elif event['RequestType'] == 'Delete':
            if use_custom_domain:
                pass
                # Don't do anything here. We do not want to delete the custom domain
                # because cognito only allows 4 custom domains per AWS account and deleting
                # custom Cognito domains doesn't free up more domains.
                # Leaving the code below just in case we want to forcefully remove a custom domain.
                #domain_obj = cognito_client.describe_user_pool_domain(Domain=custom_domain)
                #cloudfront_domain = domain_obj['DomainDescription']['CloudFrontDistribution']
                #change_resource_record_set(
                #    hosted_zone_id=hosted_zone_id, alias_target_hosted_zone_id=cloudfront_domain,
                #    record_set_dns_name=cloudfront_domain, record_set_name=custom_domain, action='DELETE')
                #delete_user_pool_domain( # Keep this around as it is expensive to create and delete.
                #    custom_domain=custom_domain, user_pool_id=user_pool_id)
            else:
                delete_resource_server(user_pool_id, resource_server_identifier)
                delete_user_pool_domain( # Keep this around as it is expensive to create and delete.
                    custom_domain=custom_domain, user_pool_id=user_pool_id)
        else:
            print('No-Op. This function should only be used on create, update, and delete stack events.')
    except Exception as e:
        print(e)
        # Change 'FAILED' to 'SUCCESS' for debugging in line below for debugging this Lambda function.
        return send_response(event, context, 'SUCCESS', response_data, reason)

    return send_response(event, context, 'SUCCESS', response_data, reason)
