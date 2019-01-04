import json
import boto3
import requests

def lambda_handler(event, context):
    print(event)
    print(json.dumps(event, indent=2))

    server = event['queryStringParameters']['server']
    request_path = server + event['path']

    response = requests.request(
        event['httpMethod']
        request_path,
        data=event['body'],
        headers=event['headers']
    )

    return {
      'statusCode': 200,
      'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      'body': response.text
    }
