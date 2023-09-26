# e-MEC API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

API Python para consulta na base de dados oficial de informações relativas às Instituições de Educação Superior (e-MEC).

Esta API faz requests e parse no Html do site do e-MEC para coletar informações sobre as instituições e os cursos de cada campus.

[e-MEC - Ministério da Educação](http://emec.mec.gov.br/)

## Instalação

A versão atual **ainda esta em fase de desenvolvimento**

Você pode baixar o código fonte do [GitHub][git] e executar:

```
python setup.py install
```

Você também pode instalar o último release estável pelo [PyPI](https://pypi.python.org/pypi)

```
pip install emec-api
```

[git]: https://github.com/pavanad/emec-api "e-MEC API"

## Dependências


Utilize o poetry para instalar as dependências do projeto.

```bash
poetry install
```

## Como usar

```python
import time
from emec.api.client import Institution

start = time.time()
ies = Institution(22)
ies.parse()
elapsed = time.time() - start
print(f"Elapsed: {elapsed}")

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
