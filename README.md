e-MEC API
=========

API Python para consulta na base de dados oficial de informações relativas às Instituições de Educação Superior (e-MEC).

Esta API faz requests e parse no Html do site do e-MEC para coletar informações sobre as instituições e os cursos de cada campus.

[emec.mec.gov.br](http://emec.mec.gov.br/)

Instalação
----------

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

Dependências
------------

As dependências do projeto estão listadas no arquivo `requirements.txt`.

```bash
pip install -r requeriments.txt
```

Como usar
---------

```python
from emec.api.client import Institution

# instancia com o codigo da ies no mec
ies = Institution(2132)

# faz o parse de todos os dados da instituicao
ies.parse()

# escreve um arquivo json com os dados coletados
ies.to_json("emec.json")
```

Outra forma de uso

```python
from emec.api.client import Institution

# instancia sem o codigo
ies = Institution()

# seta o codigo da ies
ies.set_code_ies(2132)

# faz o parse de todos os dados da instituicao
ies.parse()

# pega um json com todos os dados coletados
data = ies.get_full_data()
```
