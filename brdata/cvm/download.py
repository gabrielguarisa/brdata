import typing

import datetime
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
from bs4 import BeautifulSoup
from cachier import cachier

from brdata.utils import CACHE_DIR, get_response

URLS = {
    "dfp": "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/",
    "fca": "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/",
    "fre": "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/",
    "ipe": "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/",
    "itr": "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/",
}


def get_valid_names() -> typing.List[str]:
    """Retorna os nomes válidos de datasets da cvm"""
    return list(URLS.keys())


def get_data_urls(name: str = None) -> typing.Union[typing.Dict[str, str], str]:
    """Retorna as URLs de dados do CVM"""
    if name is None:
        return {name: f"{url}DADOS/" for name, url in URLS.items()}

    name = name.lower()
    if name not in get_valid_names():
        raise ValueError(f"{name} is not a valid name")

    return f"{URLS[name]}DADOS/"


def get_table_links(
    url: str, extension: str = ".zip", as_dict: bool = True
) -> typing.Dict[str, str]:
    """Retorna todos os links da tabela de arquivos de um dataset da cvm"""
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")

    valid_links = []

    for link_elem in soup.find_all("a"):
        link = link_elem.get("href")
        if link[-4:] == extension:
            valid_links.append(f"{url}{link}")

    if as_dict:
        return {zip_url[-8:-4]: zip_url for zip_url in valid_links}

    return valid_links


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def get_data(name: str) -> typing.Dict[str, pd.DataFrame]:
    """Baixa os arquivos de dados da cvm"""
    all_dfs = {}
    url = get_data_urls(name)

    for link in get_table_links(url, as_dict=False):
        response = get_response(link)

        with ZipFile(BytesIO(response.content)) as zip:
            filenames = zip.namelist()

            for filename in filenames:
                if filename.endswith(".csv"):
                    final_name = filename[: -len(".csv")]
                    try:
                        df = pd.read_csv(
                            zip.open(filename), delimiter=";", encoding="latin1"
                        )
                        all_dfs[final_name] = df
                    except Exception as e:
                        print("Invalid file", final_name, e)

    return all_dfs
