import json
import boto3

PUT = 'PUT'
GET = 'GET'

def lambda_handler(event, context):
    print(json.dumps(event))

    cloudformation_client = boto3.client('cloudformation')
    cloudformation_response = cloudformation_client.describe_stacks()
    print(json.dumps(cloudformation_response, indent=2, default=str))

    http_method = event['httpMethod']
    print(http_method)

    return {
      'statusCode': 200,
      'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      'body': json.dumps(cloudformation_response, indent=2, default=str)
    }
