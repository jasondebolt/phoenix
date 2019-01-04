import boto3
import sys
import json
import copy
import uuid
import requests
import airspeed

# Adds/updates finishing touches to an API Gateway API.
# This Lambda function is invoked by the API Internals CloudFormation stack.

def get_application_json(hostname, port):
    application_json_content = """
        #set($allParams = $input.params())
        {
          "requestParams" : {
            "hostname" : "%s",
            "port" : "%s",
            "path" : "$context.resourcePath",
            "method" : "$context.httpMethod"
          },
          "bodyJson" : $input.json('$'),
          "params" : {
            #foreach($type in $allParams.keySet())
              #set($params = $allParams.get($type))
              "$type" : {
                #foreach($paramName in $params.keySet())
                  "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
                  #if($foreach.hasNext),#end
                #end
              }
              #if($foreach.hasNext),#end
            #end
          },
          "stage-variables" : {
            #foreach($key in $stageVariables.keySet())
              "$key" : "$util.escapeJavaScript($stageVariables.get($key))"
              #if($foreach.hasNext),#end
            #end
          },
          "context" : {
            "account-id" : "$context.identity.accountId",
            "api-id" : "$context.apiId",
            "api-key" : "$context.identity.apiKey",
            "authorizer-principal-id" : "$context.authorizer.principalId",
            "caller" : "$context.identity.caller",
            "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
            "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
            "cognito-identity-id" : "$context.identity.cognitoIdentityId",
            "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
            "http-method" : "$context.httpMethod",
            "stage" : "$context.stage",
            "source-ip" : "$context.identity.sourceIp",
            "user" : "$context.identity.user",
            "user-agent" : "$context.identity.userAgent",
            "user-arn" : "$context.identity.userArn",
            "request-id" : "$context.requestId",
            "resource-id" : "$context.resourceId",
            "resource-path" : "$context.resourcePath"
          }
        }
    """
    application_json = airspeed.Template(
        application_json_content % (hostname, port))
    return application_json

def get_application_form_urlencoded(hostname, port):
    application_form_urlencoded_content = """
        #set($httpPost = $input.path('$').split("&"))
        {
          "requestParams" : {
            "hostname" : "%s",
            "port" : "%s",
            "path" : "$context.resourcePath",
            "method" : "$context.httpMethod"
          },
          "params" : {
            "headers": {
              #foreach($header in $input.params().header.keySet())
                "$header": "$util.escapeJavaScript($input.params().header.get($header))" #if($foreach.hasNext),#end
              #end
            }
          },
          "bodyJson" : {
            #foreach( $token in $httpPost )
              #set( $keyVal = $token.split("=") )
              #set( $keyValSize = $keyVal.size() )
              #if( $keyValSize >= 1 )
                #set( $key = $util.urlDecode($keyVal[0]) )
                #if( $keyValSize >= 2 )
                  #set( $val = $util.urlDecode($keyVal[1]) )
                #else
                  #set( $val = '' )
                #end
                "$key": "$val"#if($foreach.hasNext),#end
              #end
            #end
          },
          "stage-variables" : {
            #foreach($key in $stageVariables.keySet())
              "$key" : "$util.escapeJavaScript($stageVariables.get($key))"
              #if($foreach.hasNext),#end
            #end
          },
          "context" : {
            "account-id" : "$context.identity.accountId",
            "api-id" : "$context.apiId",
            "api-key" : "$context.identity.apiKey",
            "authorizer-principal-id" : "$context.authorizer.principalId",
            "caller" : "$context.identity.caller",
            "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
            "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
            "cognito-identity-id" : "$context.identity.cognitoIdentityId",
            "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
            "http-method" : "$context.httpMethod",
            "stage" : "$context.stage",
            "source-ip" : "$context.identity.sourceIp",
            "user" : "$context.identity.user",
            "user-agent" : "$context.identity.userAgent",
            "user-arn" : "$context.identity.userArn",
            "request-id" : "$context.requestId",
            "resource-id" : "$context.resourceId",
            "resource-path" : "$context.resourcePath"
          }
        }
    """
    application_form_urlencoded = airspeed.Template(
        application_form_urlencoded_content % (hostname, port))
    return application_form_urlencoded


client = boto3.client('apigateway')


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


def get_resource_methods(rest_api_id):
    resources_response = client.get_resources(
        restApiId=rest_api_id,
        limit=100)
    items = []
    for item in resources_response['items']:
        for method in item.get('resourceMethods', []):
            items.append({
                'id': item['id'],
                'method': method
            })
    return items


def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    response_data = {}
    lambda_version = event['ResourceProperties']['LambdaVersion']
    hostname = event['ResourceProperties']['Hostname']
    port = event['ResourceProperties']['Port']
    rest_api_id = event['ResourceProperties']['RestApiId']
    reason = 'N/A'
    resource_methods = get_resource_methods(rest_api_id)

    print('Lambda Version: {0}'.format(lambda_version))
    print(resource_methods)
    for resource_method in resource_methods:
        resource_id = resource_method['id']
        http_method = resource_method['method']
        method_response = client.get_method(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=http_method
        )

        method_uri = method_response.get('methodIntegration', {}).get('uri', '')
        if 'LambdaVPCProxy' in method_uri:
            print(method_uri)
            if 'application/json' in method_response.get('methodIntegration', {}).get('requestTemplates', ''):
                application_json_content = get_application_json(hostname, port)
                print('Adding {type} body template mapping for resource '
                      '{resource} method {method}'.format(
                          type='application/json',
                          resource=resource_id,
                          method=http_method))
                response = client.update_integration(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method,
                    patchOperations=[
                        {
                            'op': 'replace',
                            'path': '/requestTemplates/application~1json',
                            'value': application_json_content.content
                        }
                    ]
                )
            if http_method == 'POST':
                if 'application/x-www-form-urlencoded' in method_response.get('methodIntegration', {}).get('requestTemplates', ''):
                    application_form_urlencoded = get_application_form_urlencoded(hostname, port)
                    print('Adding {type} body template mapping for resource '
                          '{resource} method {method}'.format(
                              type='application/x-www-form-urlencoded',
                              resource=resource_id,
                              method=http_method))
                    response = client.update_integration(
                        restApiId=rest_api_id,
                        resourceId=resource_id,
                        httpMethod=http_method,
                        patchOperations=[
                            {
                                'op': 'replace',
                                'path': '/requestTemplates/application~1x-www-form-urlencoded',
                                'value': application_form_urlencoded.content
                            }
                        ]
                    )

    return send_response(event, context, 'SUCCESS', response_data, reason)
