# Como usar o template de Lambdas AWS?

## Onde escrever o código da sua Lambda

Os scripts Python que formam a função Lambda deverão estão dentro do diretório `app/src/`, de modo que a função principal, isto é, a função a partir da qual a Lambda será executada está no caminho `app/src/lambda_function.lambda_handler`.

## E se você precisar de pacotes que não fazem parte da biblioteca padrão do Python?
Não tem problema. Basta especificar os nomes dos pacotes no arquivo `app/requirements.txt`.

## Testar é importante
Antes de implantar uma função Lambda, é importante escrever e executar testes unitários para garantir o funcionamento da lógica por trás da função.

Por isso, a esteira de Deploy roda automaticamente os testes localizados no caminho `app/tests/` e só realiza a implantação se todos os testes forem bem sucedidos.

Para executar os testes, a esteira utiliza a biblioteca [pytest](https://docs.pytest.org/en/7.2.x/).

## Configurando sua função Lambda
Para configurar parâmetros da função Lambda, utilize o arquivo de configuração `lambda_config.yml`, localizado na raiz deste repositório.

Neste arquivo é possível especificar parâmetros como tamanho do armazenamento efêmero da função, quantidade de memória alocada, variáveis de ambiente, entre outros.

## Implantando sua função

### Pré-requisitos
- Criar uma variável de ambiente `AWS_ACCOUNT_ID`, com o ID da conta AWS onde será realizada a implantação da função. Para isso, execute o comando:
```
export AWS_ACCOUNT_ID=xxxxxxxxxxxx
```
- Configurar as credenciais DO AWS CLI. É necessário que as credenciais configuradas tenham permissão para realizar a criação da função Lambda. Para realizar a configuração do AWS CLI basta executar o seguinte comando:
```
aws configure
```

### Comando de implantação
Depois de cumprir os pré requisitos, para fazer a implantação da função lambda, basta executar o seguinte comando, a partir da raiz deste repositório:
```
bash deploy/deploy.sh [dev|prod]
```

Caso o ambiente de deploy especificado seja `dev`, o deploy será realizado de acordo com o conteúdo da branch `develop`; se o ambiente de deploy espeficiado for `prod`, o conteúdo utilizado para deploy será o da branch `main`.

