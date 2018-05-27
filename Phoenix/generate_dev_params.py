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
    what is happening here is rather simple.
    """

    # Dev pipeline template
    dev_pipeline_template = {
      "Parameters": {
        "Environment": environment_name,
        "ProjectName": "PROJECT_NAME",
        "ReviewNotificationEmail": "NOTIFICATION_EMAIL"
      }
    }
    dev_pipeline_file_obj = open('template-code-pipeline-review-params-dev.json', 'w')
    dev_pipeline_file_obj.write(json.dumps(dev_pipeline_template, indent=2))

    # Database template
    testing_database_template = _parse_json('template-database-params-testing.json')
    dev_database_template = copy.deepcopy(testing_database_template)
    # All developers will share the dev RDS instance, so we hard code 'dev'
    # rather than use the 'environment_name' here.
    dev_database_template['Parameters']['Environment'] = 'dev'
    dev_database_template['Parameters']['Vpc'] = 'dev'
    dev_database_file_obj = open('template-database-params-dev.json', 'w')
    dev_database_file_obj.write(json.dumps(dev_database_template, indent=2))

    # ECS template
    testing_ecs_template = _parse_json('template-ecs-params-testing.json')
    dev_ecs_template = copy.deepcopy(testing_ecs_template)
    dev_ecs_template['Parameters']['Environment'] = environment_name
    dev_ecs_template['Parameters']['DBEnvironment'] = 'dev'
    dev_ecs_template['Parameters']['VPCPrefix'] = 'dev'
    dev_ecs_file_obj = open('template-ecs-params-dev.json', 'w')
    dev_ecs_file_obj.write(json.dumps(dev_ecs_template, indent=2))

    # Lambda template
    testing_lambda_template = _parse_json('template-lambda-params-testing.json')
    dev_lambda_template = copy.deepcopy(testing_lambda_template)
    dev_lambda_template['Parameters']['Environment'] = environment_name
    dev_lambda_file_obj = open('template-lambda-params-dev.json', 'w')
    dev_lambda_file_obj.write(json.dumps(dev_lambda_template, indent=2))

    # API template
    testing_api_template = _parse_json('template-api-params-testing.json')
    dev_api_template = copy.deepcopy(testing_api_template)
    dev_api_template['Parameters']['Environment'] = environment_name
    dev_api_file_obj = open('template-api-params-dev.json', 'w')
    dev_api_file_obj.write(json.dumps(dev_api_template, indent=2))

    # API Deployment template
    testing_api_deployment_template = _parse_json('template-api-deployment-params-testing.json')
    dev_api_deployment_template = copy.deepcopy(testing_api_deployment_template)
    dev_api_deployment_template['Parameters']['Environment'] = environment_name
    dev_api_deployment_file_obj = open('template-api-deployment-params-dev.json', 'w')
    dev_api_deployment_file_obj.write(json.dumps(dev_api_deployment_template, indent=2))

def main(args):
    if len(args) != 1:
        raise SystemExit('Invalid arguments!')
    environment_name = args[0]
    write_dev_param_files(environment_name)

if __name__ == '__main__':
    main(sys.argv[1:])
