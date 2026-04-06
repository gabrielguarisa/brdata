from bs4 import BeautifulSoup
from typing import Literal
import requests
import os

def crawler_cvm_data(url, year):
    """
    Retorna os arquivos zip da página da cvm a partir de um filtro
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a", href=True):
            if ".zip" and year in link.text:
                link_zip = link["href"]

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao acessar {url}: {e}")

    return link_zip


def download(year: str,
            dataset: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"],  
            path: str = "data/landing/cvm", 
            overwrite: bool = False):
    
    # zip_url extract
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{dataset}/DADOS/"
    zip = crawler_cvm_data(url, year)
    full_url = url + zip

    # path setup
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, zip)

    # file check
    if overwrite == False:
        exist = os.path.isfile(full_path)
        if exist:
            return zip

    # download
    r = requests.get(full_url, stream=True)
    r.raise_for_status()

    with open(full_path, "wb") as f:
        f.write(r.content)

    return zip
