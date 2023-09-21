# e-MEC API

API Python para consulta na base de dados oficial de informações relativas às Instituições de Educação Superior (e-MEC).

Esta API faz requests e parse no Html do site do e-MEC para coletar informações sobre as instituições e os cursos de cada campus.

[emec.mec.gov.br](http://emec.mec.gov.br/)

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


As dependências do projeto estão listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
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

# export to json
ies.to_json("emec.json")

# export to csv
ies.to_csv("emec.csv")
```
