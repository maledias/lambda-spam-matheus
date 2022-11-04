from aws_lambda_typing import context as context_


def lambda_handler(event: dict, context: context_.Context):
    # Escreva o código da função aqui
    print(event)