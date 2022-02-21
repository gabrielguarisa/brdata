from typing import Dict, List

import datetime

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

METADATA_EXTENSIONS = {
    "dfp": ".zip",
    "fca": ".zip",
    "fre": ".zip",
    "ipe": ".txt",
    "itr": ".zip",
}

INVALID_SYMBOLS = [
    "000000",
    "713854",
    "8192",
    "24201A",
    "3",
    "1",
    "4030",
    "2",
    "FLEX",
    "468-5",
    "DMMO",
    "11215",
    "023175",
    "NÃO",
    "1212",
    "ADR",
    "00",
    "00000",
    "NÃO HÁ",
    "BBM",
    "022055",
    "BKBR",
    "B3",
]


def get_metadata_urls() -> Dict[str, str]:
    """Retorna as URLs de metadata do CVM"""
    return {name: f"{url}META/" for name, url in URLS.items()}


def get_data_urls() -> Dict[str, str]:
    """Retorna as URLs de dados do CVM"""
    return {name: f"{url}DADOS/" for name, url in URLS.items()}


def get_invalid_symbols() -> List[str]:
    """Retorna os símbolos inválidos conhecidos nos datasets do CVM"""
    return INVALID_SYMBOLS


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def get_table_links(
    url: str, extension: str = ".zip", as_dict: bool = True
) -> Dict[str, str]:
    """Retorna todos os links da tabela de arquivos de um dataset da cvm"""
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")

    valid_links = []

    for link_elem in soup.find_all("table")[0].find_all("a"):
        link = link_elem.get("href")
        if link[-4:] == extension:
            valid_links.append(f"{url}{link}")

    if as_dict:
        return {zip_url[-8:-4]: zip_url for zip_url in valid_links}

    return valid_links
