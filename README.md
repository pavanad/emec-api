# e-MEC API

[![PyPI Latest Release](https://img.shields.io/pypi/v/emec-api.svg)](https://pypi.org/project/emec-api/) [![PyPI Downloads](https://img.shields.io/pypi/dm/emec-api.svg?label=PyPI%20downloads)](https://pypi.org/project/emec-api/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

API Python para consulta na base de dados oficial de informações relativas às Instituições de Educação Superior (e-MEC).

Essa API faz requests e parse no Html do site do e-MEC para coletar informações sobre as instituições e os cursos de cada campus.

**IMPORTANTE:** Frequentemente o site do e-MEC fica indisponível, sendo assim verifique antes de realizar muitas requisições usando a API.

[e-MEC - Ministério da Educação](http://emec.mec.gov.br/)

## Instalação

Você pode instalar o último release estável pelo [PyPI](https://pypi.python.org/pypi)

```
pip install emec-api
```

[git]: https://github.com/pavanad/emec-api "e-MEC API"

## Dependências

Para o ambiente de desenvolvimento utilize o poetry para instalar as dependências do projeto.

```bash
poetry install
```

## Como usar

Para utilizar o pacote em seu projeto importe a classe Institution e utilize conforme abaixo:

O código da instituição de ensino pode ser localizado no site do e-MEC.

```python
from emec_api.api.client import Institution

ies = Institution(22)
ies.parse()

df_inst = ies.get_institution_dataframe()
print(df_inst.head())

df_campus = ies.get_campus_dataframe()
print(df_campus.head())

df_courses = ies.get_courses_dataframe()
print(df_courses.head())

# export to json
ies.to_json("emec.json")

# export to csv
ies.to_csv("emec.csv")
```

Para utilizar a ferramenta de linha de comando veja os exemplos abaixo:

**Comandos disponíveis**

```bash
USAGE
  emec [-h] [-q] [-v [<...>]] [-V] [--ansi] [--no-ansi] [-n] <command> [<arg1>] ... [<argN>]

ARGUMENTS
  <command>              The command to execute
  <arg>                  The arguments of the command

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                         verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question

AVAILABLE COMMANDS
  about                  Shows information about emec api
  help                   Display the manual of a command
  scraper                This command is used to scraper institutions data from emec.
```

Coletar dados da ies 4150 e exibir os dados no terminal

```bash
emec scraper --ies 4150
```

![](images/scraper.gif)

Coletar dados da ies 4150 e exportar para o formato padrão (JSON)

```bash
emec scraper --ies 4150 --output institution.json
```

![](images/scraper_output.gif)

Coletar dados da ies 4150 e exportar alterando o formato para CSV

```bash
emec scraper --ies 4150 --format csv --output institution.csv
```

Coletar dados de várias instituições usando o arquivo csv exportado pelo site do e-MEC

```
emec scraper --file list_institutions.csv
```

O arquivo de exemplo exportado pelo e-MEC pode ser encontrado [aqui](examples/data/list_institutions.csv)