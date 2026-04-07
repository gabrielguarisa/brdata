from bs4 import BeautifulSoup
from typing import Literal
from tqdm import tqdm
from datetime import date
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
                break

    except requests.exceptions.RequestException as e:
        print(f"Connection Error {url}: {e}")

    return link_zip


def download(year: int,
            dataset: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"],  
            path: str = "data/landing/cvm", 
            overwrite: bool = False):
    
    # zip_url extract
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{dataset}/DADOS/"
    zip = crawler_cvm_data(url, str(year))
    full_url = url + zip

    # path setup
    dataset_path = os.path.join(path, dataset.lower())
    os.makedirs(dataset_path, exist_ok=True)
    full_path = os.path.join(dataset_path, zip)

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

def downloads(dataset: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"], 
              start_year: int | None = None, 
              last_year: int | None = None,
              skip_exceptions: bool = True):
    
    if start_year is None and last_year is None:
        rules = {
            "ITR": (2011, 2025),
            "VLMO": (2018, 2026),
            "DFP": (2010, 2025),
            "FRE": (2010, 2026),
            "FCA": (2010, 2026)
        }
        start_year, last_year = rules.get(dataset, (start_year, last_year))
    elif last_year is None:
        last_year = date.today().year

    for year in tqdm(range(start_year, last_year+1), desc=f"Download: "):
        try:
            download(year=str(year), dataset=dataset)
        except UnboundLocalError:
            msg = f"Year {year} is invalid to {dataset}"
            if not skip_exceptions:
                raise UnboundLocalError(msg)
            tqdm.write(msg)
        
        except Exception as e:
            msg = f"Unexpected Error: {e}"
            if not skip_exceptions:
                raise e
            tqdm.write(msg)
