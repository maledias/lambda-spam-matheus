import boto3
from argparse import ArgumentParser
import yaml
import time



if __name__=='__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument('--env', type=str, required=True)
    argument_parser.add_argument('--image_uri', type=str, required=True)
    args = argument_parser.parse_args()

    # Read user defined lambda configuration
    with open("lambda_config.yml", "r") as stream:
        try:
            user_config_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    client = boto3.client('lambda')

    function_name = f"governed_lambda_{user_config_data['Parameters']['lambda_name']}-{args.env}"
    function_role = user_config_data['Parameters']['execution_role_arn']
    environment_variables = {
        'Variables': {
            var_key: var_value for var_key, var_value in user_config_data['EnvironmentVariables'][args.env].items()
        }
    }
    tags = {
        tag_key: tag_value for tag_key, tag_value in user_config_data['Tags'][args.env].items()
    }
    try:
        response = client.create_function(
            FunctionName=function_name,
            Role=function_role,
            Code={
                'ImageUri': args.image_uri
            },
            Timeout=user_config_data['Parameters']['timeout'],
            MemorySize=user_config_data['Parameters']['memory'],
            Publish=True,
            PackageType='Image',
            Environment=environment_variables,
            Tags=tags,
            Architectures=[
                'x86_64',
            ],
            EphemeralStorage={
                'Size': user_config_data['Parameters']['storage']
            }
        )
        status = 'updating'
        while status == "updating":
            time.sleep(10)
            response = client.get_function_configuration(
                FunctionName=function_name,
            )
            if response['LastUpdateStatus'] == 'Successful':
                status = 'ok'
        print("Lambda function created successfully")

    except client.exceptions.ResourceConflictException:
        print('Updating function code.')
        response = client.update_function_code(
            FunctionName=function_name,
            ImageUri=args.image_uri,
            DryRun=False,
        )
        status = 'updating'
        while status == "updating":
            time.sleep(10)
            response = client.get_function_configuration(
                FunctionName=function_name,
            )
            if response['LastUpdateStatus'] == 'Successful':
                status = 'ok'

        print('Updating function configuration')
        response = client.update_function_configuration(
            FunctionName=function_name,
            Role=function_role,
            Timeout=user_config_data['Parameters']['timeout'],
            MemorySize=user_config_data['Parameters']['memory'],
            Environment=environment_variables,
            EphemeralStorage={
                'Size': user_config_data['Parameters']['storage']
            }
        )

        status = 'updating'
        while status == "updating":
            time.sleep(10)
            response = client.get_function_configuration(
                FunctionName=function_name,
            )
            if response['LastUpdateStatus'] == 'Successful':
                status = 'ok'
        print("Lambda updated successfully")