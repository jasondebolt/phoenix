import glob
import subprocess
import boto3
import time
import os


def main():
    """
    Iterate over all cloud formation templates running validate command against them
    TODO: Stretch fork the validation into it's own process to make it faster... wait until they are all done and generate a nice report
    """
    for file_path in glob.iglob('./*.json'):
        if "params" not in file_path:
            print('Validating file: {0}'.format(file_path))

            try:
                subprocess.check_output([
                    'aws',
                    'cloudformation', 'validate-template', '--template-body',
                    'file://{0}'.format(file_path)
                ], stderr=subprocess.STDOUT)

            except subprocess.CalledProcessError as e:
                output = str(e.output)

                # If the template body is too large, it will throw an error, so instead we will need to first upload
                # the file to s3 and then validate it from there.
                if 'Member must have length less than or equal to 51200' in output:
                    print('File {0} is too large, uploading to s3 for validation'.format(file_path))

                    timestamp = str(time.time())
                    abs_path = os.path.abspath(file_path)
                    s3_file_name = timestamp + '-' + os.path.basename(abs_path)
                    s3_path = 'mosaic-phoenix-code-pipeline/{0}'.format(s3_file_name)

                    # upload the file
                    subprocess.call(['aws', 's3', 'cp', os.path.abspath(file_path), 's3://{0}'.format(s3_path)])

                    # validate the file
                    subprocess.call([
                        'aws',
                        'cloudformation', 'validate-template', '--template-url',
                        'https://s3.amazonaws.com/{0}'.format(s3_path)
                    ])

                    # delete the file
                    subprocess.call(['aws', 's3', 'rm', 's3://{0}'.format(s3_path)])
        else:
            print('Not validating parameters file: {0}'.format(file_path))


if __name__ == "__main__":
    main()
