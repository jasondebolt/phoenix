""" Generates CloudFormation JSON dev parameter files.

This script just copies all of the *params-testing.json files and generates
namespaced *params-dev.json files. Dev param files are used only by developers when
launching CloudFormation stacks during local development.

The 'environment_name' arg can be something like 'dev{username}' where
username is the developers username. When CloudFormation stacks are launched
using these parameter files, many AWS resources will be identified by this
environment_name such as URL's, ECS clusters, Lambda functions, etc.

USAGE:
  python generate_dev_params.py {environment_name}

 EXAMPLES:
  python generate_dev_params.py devjason
"""

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

import sys, os, json, copy
from glob import glob

def _parse_json(path):
    result = open(os.path.join(sys.path[0], path), 'rb').read()
    try:
        return json.loads(result)
    except json.decoder.JSONDecodeError as e:
        print('\nYour JSON is not valid! Did you check trailing commas??\n')
        raise(e)

def write_dev_param_files(environment_name):
    """ Writes the dev param files.

    I could have used loops here and made the code look less repetitive,
    but there's simply no need to optimize this or tweak any further because
    what is happening here is rather simple. Keep it simple.
    """

    # SSM environments template
    testing_ssm_environments_template = _parse_json('template-ssm-environments-params-testing.json')
    dev_ssm_environments_template = copy.deepcopy(testing_ssm_environments_template)
    dev_ssm_environments_template['Parameters']['Environment'] = environment_name
    dev_ssm_environments_template['Parameters']['Description'] = 'The dev environment is used by individual developers who full control over resources in this environment.'
    dev_ssm_environments_file_obj = open('template-ssm-environments-params-dev.json', 'w')
    dev_ssm_environments_file_obj.write(json.dumps(dev_ssm_environments_template, indent=2))

    # Database template
    testing_database_template = _parse_json('template-database-params-testing.json')
    dev_database_template = copy.deepcopy(testing_database_template)
    # All developers will share the dev RDS instance, so we hard code 'dev'
    # rather than use the 'environment_name' here.
    dev_database_template['Parameters']['Environment'] = 'dev'
    dev_database_template['Parameters']['VPCPrefix'] = 'dev'
    dev_database_file_obj = open('template-database-params-dev.json', 'w')
    dev_database_file_obj.write(json.dumps(dev_database_template, indent=2))

    # EC2 template
    testing_ec2_template = _parse_json('template-ec2-params-testing.json')
    dev_ec2_template = copy.deepcopy(testing_ec2_template)
    dev_ec2_template['Parameters']['Environment'] = environment_name
    dev_ec2_template['Parameters']['DBEnvironment'] = 'dev'
    dev_ec2_template['Parameters']['VPCPrefix'] = 'dev'
    dev_ec2_file_obj = open('template-ec2-params-dev.json', 'w')
    dev_ec2_file_obj.write(json.dumps(dev_ec2_template, indent=2))

    # Cognito template
    testing_cognito_template = _parse_json('template-cognito-params-testing.json')
    dev_cognito_template = copy.deepcopy(testing_cognito_template)
    dev_cognito_template['Parameters']['Environment'] = environment_name
    dev_cognito_file_obj = open('template-cognito-params-dev.json', 'w')
    dev_cognito_file_obj.write(json.dumps(dev_cognito_template, indent=2))

    # ECS Task Main template
    testing_ecs_task_main_template = _parse_json('template-ecs-task-main-params-testing.json')
    dev_ecs_task_main_template = copy.deepcopy(testing_ecs_task_main_template)
    dev_ecs_task_main_template['Parameters']['Environment'] = environment_name
    dev_ecs_task_main_template['Parameters']['DBEnvironment'] = 'dev'
    dev_ecs_task_main_template['Parameters']['VPCPrefix'] = 'dev'
    dev_ecs_file_obj = open('template-ecs-task-main-params-dev.json', 'w')
    dev_ecs_file_obj.write(json.dumps(dev_ecs_task_main_template, indent=2))

    # Lambda template
    testing_lambda_template = _parse_json('template-lambda-params-testing.json')
    dev_lambda_template = copy.deepcopy(testing_lambda_template)
    dev_lambda_template['Parameters']['Environment'] = environment_name
    dev_lambda_template['Parameters']['VPCPrefix'] = 'dev'
    dev_lambda_file_obj = open('template-lambda-params-dev.json', 'w')
    dev_lambda_file_obj.write(json.dumps(dev_lambda_template, indent=2))

    # API Custom Domain template
    testing_api_custom_domain_template = _parse_json(
        'template-api-custom-domain-params-testing.json')
    dev_api_custom_domain_template = copy.deepcopy(testing_api_custom_domain_template)
    dev_api_custom_domain_template['Parameters']['Environment'] = environment_name
    dev_api_custom_domain_file_obj = open('template-api-custom-domain-params-dev.json', 'w')
    dev_api_custom_domain_file_obj.write(json.dumps(dev_api_custom_domain_template, indent=2))

    # Cognito Internals template
    testing_cognito_internals_template = _parse_json('template-cognito-internals-params-testing.json')
    dev_cognito_internals_template = copy.deepcopy(testing_cognito_internals_template)
    dev_cognito_internals_template['Parameters']['Environment'] = environment_name
    dev_cognito_internals_template['Parameters']['UseCustomDomain'] = 'false' # we do not want to use custom domains for dev environments.
    dev_cognito_file_obj = open('template-cognito-internals-params-dev.json', 'w')
    dev_cognito_file_obj.write(json.dumps(dev_cognito_internals_template, indent=2))

    # API template
    testing_api_template = _parse_json('template-api-params-testing.json')
    dev_api_template = copy.deepcopy(testing_api_template)
    dev_api_template['Parameters']['Environment'] = environment_name
    dev_api_template['Parameters']['VPCPrefix'] = 'dev'
    dev_api_file_obj = open('template-api-params-dev.json', 'w')
    dev_api_file_obj.write(json.dumps(dev_api_template, indent=2))

    # API Deployment template
    testing_api_deployment_template = _parse_json('template-api-deployment-params-testing.json')
    dev_api_deployment_template = copy.deepcopy(testing_api_deployment_template)
    dev_api_deployment_template['Parameters']['Environment'] = environment_name
    dev_api_deployment_file_obj = open('template-api-deployment-params-dev.json', 'w')
    dev_api_deployment_file_obj.write(json.dumps(dev_api_deployment_template, indent=2))

    # API Documentation buckets templates
    for testing_file in glob('template-api-documentation-v*-params-testing.json'):
        testing_api_docs_bucket_template = _parse_json(testing_file)
        dev_api_docs_bucket_template = copy.deepcopy(testing_api_docs_bucket_template)
        dev_api_docs_bucket_template['Parameters']['DomainPrefix'] = dev_api_docs_bucket_template[
            'Parameters']['DomainPrefix'].replace('testing', environment_name)
        dev_api_docs_bucket_template['Parameters']['Environment'] = environment_name
        dev_file = testing_file.replace('testing', 'dev')
        dev_api_docs_bucket_file_obj = open(dev_file, 'w')
        dev_api_docs_bucket_file_obj.write(json.dumps(dev_api_docs_bucket_template, indent=2))

def main(args):
    if len(args) != 1:
        raise SystemExit('Invalid arguments!')
    environment_name = args[0]
    write_dev_param_files(environment_name)

if __name__ == '__main__':
    main(sys.argv[1:])
