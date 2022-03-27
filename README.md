<p align="center">
  <a href="https://github.com/gabrielguarisa/brdata"><img src="https://raw.githubusercontent.com/gabrielguarisa/brdata/0bd34000bf29bd5b93aee011f368bc0385680c58/logo.png?token=GHSAT0AAAAAABPPKYT7BQBOVDJG3NYYQKNOYQ5JIZA" alt="brdata"></a>
</p>
<p align="center">
    <em>Fontes de dados do mercado financeiro brasileiro</em>
</p>

<div align="center">

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

Baixando os arquivos de dados:

```python
cvm.download_data("data")
```

Baixando os arquivos de metadados:

```python
cvm.download_metadata("data")
```

#### Formulário Cadastral

Usando dados do [formulário cadastral](https://dados.gov.br/dataset/cia_aberta-doc-fca):

```python
g_fca = cvm.GeralFCA("data")
vm_fca = cvm.ValorMobiliarioFCA("data")
```

Consultando dados para uma determinada companhia:

```python
g_fca.get_cia(cvm_code=14460)
# OU
g_fca.get_cia(cnpj="47.960.950/0001-21")
```

Número de companhias cadastradas por ano:

```python
g_fca.get_num_cias_per_year()
```

Quantidade de empresas cadastradas por setor em cada ano:

```python
g_fca.get_sectors_per_year()
```

#### Formulário de Referência

Usando dados do [formulário de referência](https://dados.gov.br/dataset/cia_aberta-doc-fre):

```python
cvm.DistribuicaoCapitalFRE("data")
```

Consultando dados para uma determinada companhia:

```python
d_fre.get_cia("47.960.950/0001-21")
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
b3.all_companies()
```

Listando todas as BDRs disponíveis:

```python
b3.all_bdrs()
```

Detalhamento de uma empresa:

```python
b3.company_detail(cvm_code="25135")
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