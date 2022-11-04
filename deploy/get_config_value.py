from argparse import ArgumentParser
import yaml


if __name__=='__main__':
    
    argument_parser  = ArgumentParser()
    argument_parser.add_argument('--config', type=str, required=True)
    args = argument_parser.parse_args()

    with open("lambda_config.yml", "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    print(data['Parameters'][args.config])