import requests
from datetime import date
from typing import Literal

from .utils import write_to_disk

def fetch_selic(
        category: Literal["meta", "diaria"],
        start_date: str = None,
        end_date: str = None,
        path: str = None
):
    
    """
    Fetches 'Selic Meta' or 'Selic Diária' data.
    It can be downloaded directly if a file path is provided.
    \nDate format: str = 'dd/mm/yyyy'
    \n- The difference between the start and end dates cannot exceed 10 years.
    """
    start_date = start_date or date.today().strftime('%d/%m/%Y')

    if category == "meta":
        url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"
        filename = f"selic_meta_{start_date.replace("/", "-")}.json"
    else:
        url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
        filename = f"selic_diaria_{start_date.replace("/", "-")}.json"

    params = {
        "formato": "json",
        "dataInicial": start_date
    }
    if end_date:
        params["dataFinal"] = end_date

    try:
        response = requests.get(url_bcb, params=params)
        response.raise_for_status()
        data = response.json()
        if path:
            write_to_disk(data, filename, path)
        else:
            return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

__all__ = [
    "fetch_meta"
]