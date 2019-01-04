""" Generates CloudFormation JSON environment specific parameter files.

This script just copies all of the *params-testing.json files and generates
namespaced *-params-{environment}.json files. If the '--delete' flag is passed
in, all files matching *-params-{environment}.json will be deleted.

Typically you'll only need to run this script once per new environment. It is
a utility script to make is easier to generate all of the cloudformation
parameter files for a new environment.

The 'environment' arg can be something like 'staging' or 'rc'.
When CloudFormation stacks are launched using these parameter files,
all AWS resources will be identified by this environment such as
URL's, ECS clusters, Lambda functions, etc.

USAGE:
  python generate_environment_params.py {environment}
  python generate_environment_params.py {environment} --delete

 EXAMPLES:
  python generate_environment_params.py staging
  python generate_environment_params.py staging --delete
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

def delete_environment_param_files(environment):
    for filename in glob('*-params-{0}.json'.format(environment)):
        os.remove(filename)

def write_environment_param_files(environment):
    """ Writes the environment param files.

    I could have used loops here and made the code look less repetitive,
    but there's simply no need to optimize this or tweak any further because
    what is happening here is rather simple. Keep it simple.
    """

    # SSM environments template
    testing_ssm_environments_template = _parse_json('template-ssm-environments-params-testing.json')
    env_ssm_environments_template = copy.deepcopy(testing_ssm_environments_template)
    env_ssm_environments_template['Parameters']['Environment'] = environment
    env_ssm_environments_template['Parameters']['Description'] = 'The {0} environment'.format(environment)
    env_ssm_environments_file_obj = open('template-ssm-environments-params-{0}.json'.format(environment), 'w')
    env_ssm_environments_file_obj.write(json.dumps(env_ssm_environments_template, indent=2))

    # Database template
    testing_database_template = _parse_json('template-database-params-testing.json')
    env_database_template = copy.deepcopy(testing_database_template)
    env_database_template['Parameters']['Environment'] = environment
    env_database_file_obj = open('template-database-params-{0}.json'.format(environment), 'w')
    env_database_file_obj.write(json.dumps(env_database_template, indent=2))

    # EC2 template
    testing_ec2_template = _parse_json('template-ec2-params-testing.json')
    env_ec2_template = copy.deepcopy(testing_ec2_template)
    env_ec2_template['Parameters']['Environment'] = environment
    env_ec2_template['Parameters']['DBEnvironment'] = environment
    env_ec2_file_obj = open('template-ec2-params-{0}.json'.format(environment), 'w')
    env_ec2_file_obj.write(json.dumps(env_ec2_template, indent=2))

    # Cognito template
    testing_cognito_template = _parse_json('template-cognito-params-testing.json')
    env_cognito_template = copy.deepcopy(testing_cognito_template)
    env_cognito_template['Parameters']['Environment'] = environment
    env_cognito_file_obj = open('template-cognito-params-{0}.json'.format(environment), 'w')
    env_cognito_file_obj.write(json.dumps(env_cognito_template, indent=2))

    # ECS Task Main template
    testing_ecs_task_main_template = _parse_json('template-ecs-task-main-params-testing.json')
    env_ecs_task_main_template = copy.deepcopy(testing_ecs_task_main_template)
    env_ecs_task_main_template['Parameters']['Environment'] = environment
    env_ecs_task_main_template['Parameters']['DBEnvironment'] = environment
    env_ecs_file_obj = open('template-ecs-task-main-params-{0}.json'.format(environment), 'w')
    env_ecs_file_obj.write(json.dumps(env_ecs_task_main_template, indent=2))

    # Lambda template
    testing_lambda_template = _parse_json('template-lambda-params-testing.json')
    env_lambda_template = copy.deepcopy(testing_lambda_template)
    env_lambda_template['Parameters']['Environment'] = environment
    env_lambda_file_obj = open('template-lambda-params-{0}.json'.format(environment), 'w')
    env_lambda_file_obj.write(json.dumps(env_lambda_template, indent=2))

    # API Custom Domain template
    testing_api_custom_domain_template = _parse_json('template-api-custom-domain-params-testing.json')
    env_api_custom_domain_template = copy.deepcopy(testing_api_custom_domain_template)
    env_api_custom_domain_template['Parameters']['Environment'] = environment
    env_api_custom_domain_file_obj = open('template-api-custom-domain-params-{0}.json'.format(environment), 'w')
    env_api_custom_domain_file_obj.write(json.dumps(env_api_custom_domain_template, indent=2))

    # Cognito Internals template
    testing_cognito_internals_template = _parse_json('template-cognito-internals-params-testing.json')
    env_cognito_internals_template = copy.deepcopy(testing_cognito_internals_template)
    env_cognito_internals_template['Parameters']['Environment'] = environment
    env_cognito_internals_template['Parameters']['UseCustomDomain'] = 'false' # we do not want to use custom domains for dev environments.
    env_cognito_file_obj = open('template-cognito-internals-params-{0}.json'.format(environment), 'w')
    env_cognito_file_obj.write(json.dumps(env_cognito_internals_template, indent=2))

    # API template
    testing_api_template = _parse_json('template-api-params-testing.json')
    env_api_template = copy.deepcopy(testing_api_template)
    env_api_template['Parameters']['Environment'] = environment
    env_api_file_obj = open('template-api-params-{0}.json'.format(environment), 'w')
    env_api_file_obj.write(json.dumps(env_api_template, indent=2))

    # API Deployment template
    testing_api_deployment_template = _parse_json('template-api-deployment-params-testing.json')
    env_api_deployment_template = copy.deepcopy(testing_api_deployment_template)
    env_api_deployment_template['Parameters']['Environment'] = environment
    env_api_deployment_file_obj = open('template-api-deployment-params-{0}.json'.format(environment), 'w')
    env_api_deployment_file_obj.write(json.dumps(env_api_deployment_template, indent=2))

    # API Documentation buckets templates
    for testing_file in glob('template-api-documentation-v*-params-testing.json'):
        testing_api_docs_bucket_template = _parse_json(testing_file)
        env_api_docs_bucket_template = copy.deepcopy(testing_api_docs_bucket_template)
        env_api_docs_bucket_template['Parameters']['DomainPrefix'] = env_api_docs_bucket_template[
            'Parameters']['DomainPrefix'].replace('testing', environment)
        env_api_docs_bucket_template['Parameters']['Environment'] = environment
        env_file = testing_file.replace('testing', environment)
        env_api_docs_bucket_file_obj = open(env_file, 'w')
        env_api_docs_bucket_file_obj.write(json.dumps(env_api_docs_bucket_template, indent=2))

def main(args):
    if len(args) == 2 and args[1] == '--delete':
        environment = args[0]
        print("Deleting files")
        delete_environment_param_files(environment)
    elif len(args) != 1:
        raise SystemExit('Invalid arguments!')
    else:
        environment = args[0]
        print("Writing files")
        write_environment_param_files(environment)

if __name__ == '__main__':
    main(sys.argv[1:])
