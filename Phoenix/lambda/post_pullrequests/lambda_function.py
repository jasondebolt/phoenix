import os
import json
import boto3
import botocore
import requests
from datetime import datetime
import zipfile
import tempfile
import urllib.parse
from boto3.session import Session

# Handles the final stages of the pull request pipeline, after all tests pass and the ECS container is deployed.

ssm_client = boto3.client('ssm')
code_pipeline_client = boto3.client('codepipeline')

GITHUB_API_URL = 'https://api.github.com'

class JSONObject:
  def __init__(self, dict):
      vars(self).update(dict)

# Assign python values to values return from github JSON reqeuest object
false = False
true = True
null = None

def get_github_access_token():
    print('getting github access token')
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/github/access-token'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_microservice_bucket_name():
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/bucket-name'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_microservice_domain():
    response = ssm_client.get_parameter(
        Name='/microservice/{0}/global/domain'.format(os.environ['PROJECT_NAME']),
        WithDecryption=True
    )
    return response['Parameter']['Value']

def notify_github(pull_request_number, request_body):
    url = os.path.join(GITHUB_API_URL, 'repos/{0}/{1}/issues/{2}/comments'.format(
        os.environ['GITHUB_ORGANIZATION'], os.environ['PROJECT_NAME'], pull_request_number))
    payload = { "body": request_body }
    headers = {'Authorization': 'token {0}'.format(get_github_access_token())}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(json.dumps(response.json(), indent=2))

def find_artifact(artifacts, name):
    """Finds the artifact 'name' among the 'artifacts'

    Args:
        artifacts: The list of artifacts available to the function
        name: The artifact we wish to use
    Returns:
        The artifact dictionary found
    Raises:
        Exception: If no matching artifact is found

    """
    for artifact in artifacts:
        if artifact['name'] == name:
            return artifact

    raise Exception('Input artifact named "{0}" not found in event'.format(name))

def get_user_params(job_data):
    """Decodes the JSON user parameters and validates the required properties.

    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure

    Returns:
        The JSON parameters decoded as a dictionary.

    Raises:
        Exception: The JSON can't be decoded or a property is missing.

    """
    try:
        # Get the user parameters which contain the stack, artifact and file settings
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)

    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception('UserParameters could not be decoded as JSON')

    if 'artifact' not in decoded_parameters:
        # Validate that the artifact name is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the artifact name')

    return decoded_parameters

def setup_s3_client(job_data):
    """Creates an S3 client

    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.

    Args:
        job_data: The job data structure

    Returns:
        An S3 client with the appropriate credentials

    """
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']

    session = Session(aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))

def get_file_as_string(s3, artifact, file_in_zip):
    """Gets the file artifact

    Downloads the artifact from the S3 artifact store to a temporary file
    then extracts the zip and returns the file containing the GitHub info.

    Args:
        artifact: The artifact to download
        file_in_zip: The path to the file within the zip containing the template

    Returns:
        The file as a string

    Raises:
        Exception: Any exception thrown while downloading the artifact or unzipping it

    """
    tmp_file = tempfile.NamedTemporaryFile()
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']

    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            return zip.read(file_in_zip)

def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    """
    print('Putting job success')
    print(message)
    code_pipeline_client.put_job_success_result(jobId=job)

def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    """
    print('Putting job failure')
    print(message)
    code_pipeline_client.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})

def lambda_handler(event, context):
    try:
        print(event)
        json_obj = json.dumps(event, indent=4)
        print(json_obj)
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        params = get_user_params(job_data)
        artifacts = job_data['inputArtifacts']
        artifact = params['artifact'] # The actual name of the CodePipeline artifact, such as 'MyApp' or 'SourceOutput'
        file_name = params['file'] # The name of the file you want to access
        artifact_data = find_artifact(artifacts, artifact)
        s3 = setup_s3_client(job_data)
        file_str = get_file_as_string(s3, artifact_data, file_name)
        data_obj = json.loads(file_str.decode('utf-8'))
        print("data_obj: ")
        print(data_obj)

        repo_name = data_obj['RepoName']
        source_branch = data_obj['SourceBranch']
        pull_request_number = data_obj['PullRequestNumber']
        source_version = data_obj['SourceVersion']

        bucket_name = get_microservice_bucket_name()
        domain = get_microservice_domain()

        # Notify github
        region = os.environ['AWS_DEFAULT_REGION']
        ecs_url = 'https://mr-{source_version}.ecs.{domain}'.format(
            source_version=source_version, domain=domain)
        request_body = (
            'View deployed container (<a href="{0}">{1}</a>) @ commit {2}'.format(
                ecs_url, ecs_url, source_version))
        notify_github(pull_request_number, request_body)

        # We must notify CodePipeline of the job status or it will block the pipeline for ages
        put_job_success(job_id, 'Function complete')
    except Exception as e:
        print('Function failed due to exception.')

        # We must notify CodePipeline of the job status or it will block the pipeline for ages
        put_job_failure(job_id, 'Function failed')
        print(e)

    print('Function complete.')
    return "Complete."
