<p align="center">
  <a href="https://github.com/gabrielguarisa/brdata"><img src="https://raw.githubusercontent.com/gabrielguarisa/brdata/0bd34000bf29bd5b93aee011f368bc0385680c58/logo.png?token=GHSAT0AAAAAABPPKYT7BQBOVDJG3NYYQKNOYQ5JIZA" alt="brdata"></a>
</p>
<p align="center">
    <em>Fontes de dados do mercado financeiro brasileiro</em>
</p>

## Instalação
```shell
pip install brasil-data
```

## Como usar
Após a instalação você pode importar a biblioteca diretamente para seu código:
```Python
import brdata
```

### O que *brdata* faz?
- `brdata.b3`: Extrai índices da B3.
	- `b3.list_indexes()`: Lista os índices da B3 disponíveis.
	- `b3.download_index(valid_index, path=None, theoretical=True)`: Retorna os dados de um índice ou salva o JSON quando `path` é informado. Use `theoretical=False` para a carteira do dia.
	- `b3.download_indexes(index_list: list[str], path=None, theoretical=True)`: Retorna os dados de uma lista de índices válidos ou salva os JSONs quando `path` é informado. Use `theoretical=False` para a carteira do dia.

- `brdata.cvm`: Download de formulários da CVM `(DFP, ITR, FRE, FCA, VLMO)` .
	- `cvm.dataset(year, dataset_type)`: Baixa um dataset baseado no ano.
	- `cvm.datasets_in_range(dataset_type, start_year, last_year)`: Baixa uma série de datasets dentro de um range de anos.

## Colaboradores
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/gabrielguarisa">
        <img src="https://github.com/gabrielguarisa.png" width="100px;" alt="Foto do Gabriel"/><br>
        <sub><b>Gabriel Guarisa</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/daviguarisa">
        <img src="https://github.com/daviguarisa.png" width="100px;" alt="Foto do Davi"/><br>
        <sub><b>Davi Guarisa</b></sub>
      </a>
    </td>
  </tr>
</table>
