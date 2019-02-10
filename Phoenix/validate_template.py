import glob
import subprocess
import time
import os


def infra_status(cmd, status):
    if status != 0:
        text = 'Error: Running \n{0}\n '.format(cmd)
        print(text)
        exit(0)

def make_bucket(bucket):
    """Check if the bucket already exists, if not then create it"""
    ret = subprocess.call(['aws', 's3', 'ls', 's3://{0}'.format(bucket)])

    if ret != 0:
      subprocess.call(['aws', 's3', 'mb', 's3://{0}'.format(bucket)])

def main():
    """
    Iterate over all cloud formation templates running validate command against them
    TODO: Stretch fork the validation into it's own process to make it faster... wait until they are all done and generate a nice report
    """
    for file_path in glob.iglob('**/*.json'):
        if "params" not in file_path:
            print('Validating file: {0}'.format(file_path))

            try:
               result = subprocess.call([
                   'aws',
                   'cloudformation', 'validate-template', '--template-body',
                   'file://{0}'.format(file_path)
               ])
               if result != 0:
                 # If this valdate throughs as expection it is caught but if it just puts and error
                 # in the output then we have false positives. That is why I have the one about.
                 # I feel my logic is flawed.
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
                    s3_file_name = timestamp.split('.')[0] + '-' + os.path.basename(abs_path)
                    bucket = 'infratemp' + timestamp.split('.')[0]

                    make_bucket(bucket)
                    s3_path = '{0}/{1}'.format(bucket, s3_file_name)

                # upload the file
                    ret = subprocess.call(['aws', 's3', 'cp', os.path.abspath(file_path), 's3://{0}'.format(s3_path)])
                    cmd = 'aws s3 cp {0} s3://{1}'.format(os.path.abspath(file_path), s3_path )
                    infra_status(cmd, ret)

                    # validate the file
                    result = subprocess.call([
                        'aws',
                        'cloudformation', 'validate-template', '--template-url',
                        'https://s3.amazonaws.com/{0}'.format(s3_path)
                    ])

                    # delete the file
                    ret = subprocess.call(['aws', 's3', 'rm', 's3://{0}'.format(s3_path)])
                    cmd =  'aws s3 rm s3://{0}'.format( s3_path )
                    infra_status( cmd, ret)

                    # delete the bucket
                    ret = subprocess.call(['aws', 's3', 'rb', '--force', 's3://{0}'.format(bucket)])
                    cmd =  'aws s3 rb --force s3://{0}'.format( bucket )
                    infra_status( cmd, ret)


                    if result != 0:
                        text = 'Validation failed! aws cloudformation validate-template --template-url https://s3.amazonaws.com/{0}'.format(s3_path)
                        print(text)
                        exit(1)

            except : #need to catch other exceptions
                text = 'Exception: Validation failed! aws cloudformation validate-template --template-body file://{0}'.format(file_path)
                print(text)
                exit(1)
            if result != 0:
                text = 'Exception: Validation failed! aws cloudformation validate-template --template-body file://{0}'.format(file_path)
                print(text)
                exit(1)

    print('\n\nAll cloudformation have valid syntax. Nice job you ROCK!!\n\n')


if __name__ == "__main__":
    main()
