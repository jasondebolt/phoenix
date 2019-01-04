""" Converts CloudFormation parameters to the native format expected by the CLI.

Code Pipeline expects this format:
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html#w2ab2c13c15c13

CloudFormation expects this format:
https://aws.amazon.com/blogs/devops/passing-parameters-to-cloudformation-stacks-with-the-aws-cli-and-powershell/

USAGE:
  python parameters_generator.py template.json {cloudformation | codepipeline} > temp.json

  The input format of the template.json file is the codepipeline format.

  Use to the temp.json file at a parameter file in a cloudformation CLI call:
  aws cloudformation create-stack --stack-name <stack_name> --template-body file://template.json --parameters file://temp.json

  OR

  Use to the temp.json file at a parameter file in a codepipeline deployment action.
"""

__author__ = "Jason DeBolt (jasondebolt@gmail.com)"

import sys, os, json

def convert_parameters_file(obj, conversion_format='cloudformation'):
    params = obj['Parameters']
    cloudformation_obj = []
    codepipeline_obj = {'Parameters': {}}

    project_name = _parse_json(
        'template-ssm-globals-macro-params.json')['Parameters']['ProjectName']

    for param_key in params:
        value = params[param_key]
        if 'PROJECT_NAME_NO_DASHES' in value:
            # Removes dashes
            value = value.replace('PROJECT_NAME_NO_DASHES', project_name.replace('-', ''))[:7]
        elif 'PROJECT_NAME' in value:
            value = value.replace('PROJECT_NAME', project_name)

        if conversion_format == 'cloudformation':
            cloudformation_obj.append({'ParameterKey': param_key, 'ParameterValue': value})
        elif conversion_format == 'codepipeline':
            codepipeline_obj['Parameters'][param_key] = value
        else:
            raise SystemExit('Invalid conversion_format: {0}'.format(
                conversion_format))
    return json.dumps(cloudformation_obj or codepipeline_obj, indent=4)

def _parse_json(path):
    result = open(os.path.join(sys.path[0], path), 'rb').read()
    try:
        return json.loads(result)
    except json.decoder.JSONDecodeError as e:
        print('\nYour JSON is not valid! Did you check trailing commas??\n')
        raise(e)

def main(args):
    if len(args) != 2 or args[1] not in ['cloudformation', 'codepipeline']:
        raise SystemExit('Invalid arguments!')
    params_file = args[0]
    conversion_format = args[1]
    json_result = _parse_json(params_file)
    print(convert_parameters_file(json_result, conversion_format))

if __name__ == '__main__':
    main(sys.argv[1:])
