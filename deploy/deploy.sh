#!/bin/bash

# exit when any command fails
set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

function exists_in_list() {
    LIST=$1
    DELIMITER=$2
    VALUE=$3
    LIST_WHITESPACES=`echo $LIST | tr "$DELIMITER" " "`
    for x in $LIST_WHITESPACES; do
        if [ "$x" = "$VALUE" ]; then
            return 0
        fi
    done
    return 1
}

echo "Iniciando processo de Deploy."

# Checa se o argumento de linha de comando foi recebido
# e se este é válido

ENV=$1
build_hash=$RANDOM
valid_environments="dev prod"

if [[ -z $ENV ]];
then 
    echo "ERRO! - O ambiente de Deploy não foi fornecido."
    exit 1
else
    if exists_in_list "$valid_environments" " " $ENV; then
        echo "Iniciando o processo de Deploy no ambiente $ENV"
    else
        echo "Ambiente inválido: $ENV"
        exit 1
    fi
fi

if [[ $ENV == "prod" ]] ; then
    git checkout main
else
    git checkout develop
fi

# Cria ambiente virtual temporário e instala pacotes para execução de testes

echo "Criando ambiente virtual temporário"
python -m venv /tmp/$build_hash/env
source /tmp/$build_hash/env/bin/activate

echo "Instalando pacotes de Deploy"
python3 -m pip install -r deploy/requirements.txt

echo "Instalando pacotes app"
python3 -m pip install -r app/requirements.txt

echo "Executando testes unitários"
python3 -m pytest app/tests/

if [[ !( "$?" == 0 ) ]] ; then
    echo "Testes falharam."
    exit 1
else
    echo "Testes unitários executados com sucesso."
fi



# Cria imagem Docker da Lambda e envia para repositório no ECR

echo "Get AWS ECR Credentials"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

echo "Creating AWS ECR repository if it does not exists."
lambda_name=$(python -m deploy.get_config_value --config lambda_name)
REPO_NAME=governed_lambda_ecr_repo_${lambda_name}_${ENV}
aws ecr describe-repositories --repository-names ${REPO_NAME} > /dev/null  || aws ecr create-repository --repository-name ${REPO_NAME} > /dev/null

echo "Building Lambda Docker image"
docker_image_name=${lambda_name}_${ENV}_image:latest
docker build -t ${docker_image_name} app/

echo "Pushing image to ECR"
docker tag  ${docker_image_name} ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${REPO_NAME}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${REPO_NAME}:latest

echo "Deploying the Lambda function"
python -m deploy.deploy  --env $ENV --image_uri ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${REPO_NAME}:latest

echo "Fim do processo de Deploy"
exit 0 

