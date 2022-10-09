<p align="center">
  <a href="https://github.com/gabrielguarisa/brdata"><img src="https://raw.githubusercontent.com/gabrielguarisa/brdata/0bd34000bf29bd5b93aee011f368bc0385680c58/logo.png?token=GHSAT0AAAAAABPPKYT7BQBOVDJG3NYYQKNOYQ5JIZA" alt="brdata"></a>
</p>
<p align="center">
    <em>Fontes de dados do mercado financeiro brasileiro</em>
</p>

<div align="center">

[![Package version](https://img.shields.io/pypi/v/brasil-data?color=%2334D058&label=pypi%20package)](https://pypi.org/project/brasil-data/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/gabrielguarisa/brdata/releases)
[![License](https://img.shields.io/github/license/gabrielguarisa/brdata)](https://github.com/gabrielguarisa/brdata/blob/main/LICENSE)

</div>

## Instalação

```shell
pip install brasil-data
```

## Utilização

### XPI

Coletando dados da análise da XPI para uma determinada ação:

```python
from brdata import xpi
xpi.analise("cyre3")
```

### Fundamentus

Coletando tabela do resultado da busca no Fundamentus (equivalenta a página https://www.fundamentus.com.br/resultado.php):

```python
from brdata import fundamentus
fundamentus.resultados()
```

Balanços históricos de uma determinada ação:

```python
balanco, demonstrativo = fundamentus.balanco_historico("mglu3")
```

Detalhes de uma ação:

```python
fundamentus.detalhes("mglu3")
```

### CVM


Importando módulo:

```python
from brdata import cvm
```

Baixando os dados para um determinado tipo de prefixo:

```python
cvm.get_data(prefix)
```

Obtendo os valores válidos para o parâmetro `prefix`:

```python
cvm.get_valid_prefixes()
# ['dfp', 'fca', 'fre', 'ipe', 'itr']
```

Consumindo os valores dos formulários para cada um dos prefixos:

```python
r = cvm.Reader(prefix)

Consultando anos disponíveis de dados:

```python
r.years
```

#### Formulário Cadastral (FCA)

Usando dados do [formulário cadastral](https://dados.gov.br/dataset/cia_aberta-doc-fca):

```python
fca = cvm.Reader("fca")
```

Consumindo dados históricos de uma determinada empresa num determinado formulário (`form_name`):

```python
fca.processors[form_name].get_cia_history("47.960.950/0001-21")
```

Consumindo os dados mais recentes para cada uma das empresas num determinado formulário (`form_name`):

```python
fca.processors[form_name].get_most_recent()
```

Consultando valores válidos para `form_name`:

```python
fca.forms
```

### B3

Importando módulo:

```python
from brdata import b3
```

Índices disponíveis:

```python
b3.indices()
```

Coletando composição de um índice:

```python
b3.portfolio("ibov")
```

Listando empresas disponíveis na B3:

```python
b3.cias()
```

Listando todas as BDRs disponíveis:

```python
b3.bdrs()
```

Detalhamento de uma empresa:

```python
b3.detalhes(cvm_code="25135")
```

### Valor Econômico

Importando módulo:

```python
from brdata import valor
```

Portfólios das instituições financeiras:

```python
valor.portfolios(2, 2022)
```

Carteira Valor:

```python
valor.carteira_valor(2, 2022)
```

## Contribuindo com o projeto

Para contribuir com o projeto, consulte o [guia de contribuição](https://github.com/gabrielguarisa/brdata/blob/main/CONTRIBUTING.md).