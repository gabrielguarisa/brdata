from bs4 import BeautifulSoup
from typing import Literal
from tqdm import tqdm
from datetime import date
import requests
import os

DEFAULT_RULES = {
            "ITR": (2011, 2025),
            "VLMO": (2018, 2026),
            "DFP": (2010, 2025),
            "FRE": (2010, 2026),
            "FCA": (2010, 2026)
        }

def crawler(url, year: int = None):
    """Returns the zip files from the CVM page based on a filter"""
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text()
            if href.endswith(".zip"):
                if year:
                    if str(year) in text:
                        return href
                else:
                    return href
    
    except requests.exceptions.RequestException as e:
        print(f"Connection Error {url}: {e}")
    return None


def dataset(year: int,
            dataset_type: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"],  
            path: str = "data/landing/cvm", 
            overwrite: bool = False):
    """Download a dataset from the CVM based on your year"""
    try:
        # zip_url extract
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{dataset_type}/DADOS/"
        zip = crawler(url, str(year))
        if zip is None:
            raise Exception("File not found!")
        
        full_url = url + zip

        # path setup
        dataset_path = os.path.join(path, dataset_type.lower())
        os.makedirs(dataset_path, exist_ok=True)
        full_path = os.path.join(dataset_path, zip)

        # file check
        if not overwrite:
            exist = os.path.isfile(full_path)
            if exist:
                return zip

        # download
        r = requests.get(full_url, stream=True)
        r.raise_for_status()

        with open(full_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        return zip
    
    except Exception as e:
        raise Exception(f"Download Failure ({dataset_type} {year})") from None

def datasets_in_range(dataset_type: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"], 
              start_year: int | None = None, 
              last_year: int | None = None,
              skip_exceptions: bool = True):
    """Download CVM datasets within a range of years"""
    if start_year is None and last_year is None:
        start_year, last_year = DEFAULT_RULES.get(dataset_type, (start_year, last_year))
    elif last_year is None:
        last_year = date.today().year

    for year in tqdm(range(start_year, last_year+1), desc=f"Download: "):
        try:
            dataset(year=str(year), dataset_type=dataset_type)
        except Exception as e:
            if not skip_exceptions:
                raise e
            tqdm.write(str(e))

def metadata_dataset(dataset_type: Literal["ITR", "DFP", "VLMO", "FRE", "FCA"]):
    """Download metadate for CVM datasets"""
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{dataset_type}/META/"
    zip = crawler(url)
    if zip is None:
        raise Exception("File Not Found!")

    full_url = url + zip
    path = "data/landing/cvm/metadata"
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, zip)

    response = requests.get(full_url, stream=True)
    response.raise_for_status()

    with open(full_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)