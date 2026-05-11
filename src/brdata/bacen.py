import requests
import os
import json
from datetime import date
from typing import Literal, TypeAlias

def selic_meta(start_date: str = None,
               end_date: str = None,
               path: str = "data/landing/bacen"):
    
    """
    Search for 'Selic Meta' data using a date filter.
    Date format: str = 'dd/mm/yyyy'
    """
    start_date = start_date or date.today().strftime('%d/%m/%Y')
    os.makedirs(path, exist_ok=True)
    file_name = f"selic_meta_{start_date.replace("/", "-")}.json"
    full_path = os.path.join(path, file_name)

    url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"
    params = {
        "formato": "json",
        "dataInicial": start_date
    }
    if end_date:
        params["dataFinal"] = end_date

    try:
        response = requests.get(url_bcb, params=params)
        response.raise_for_status()

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)

        print(f"Download {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

CodigosFocus: TypeAlias = Literal[
    "ExpectativaMercadoMensais", "ExpectativasMercadoSelic", "ExpectativasMercadoTrimestrais",
    "ExpectativasMercadoAnuais", "ExpectativasMercadoInflacao12Meses",
    "ExpectativasMercadoInflacao24Meses", "ExpectativasMercadoTop5Mensais",
    "ExpectativasMercadoTop5Selic", "ExpectativaMercadoTop5Trimestral", 
    "ExpectativasMercadoTop5Anuais", "ExpectativasMercadoTop5Inflacao12Meses",
    "ExpectativasMercadoTop5Inflacao24Meses", 
    "DatasReferencia"
]
def boletim_focus(
        cod: CodigosFocus,
        path: str = "data/landing/bacen/boletimfocus"
        ):
    url = f"https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/{cod}?$format=json"
    os.makedirs(path, exist_ok=True)
    filename = f"boletim_focus_{cod}.json"
    full_path = os.path.join(path, filename)

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
        print(f"Download {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
