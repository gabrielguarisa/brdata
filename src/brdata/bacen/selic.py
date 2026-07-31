import requests
from datetime import date, datetime
from typing import Literal

from .utils import write_to_disk, date_validator

def fetch_selic(
    category: Literal["meta", "diaria"],
    start_date: str = None,
    end_date: str = None,
    path: str = None
):
    """
    Fetches 'Selic Meta' or 'Selic Diária' data.
    It can be downloaded directly if a file path is provided.
    
    Date format: str = 'YYYY-MM-DD'
    - The difference between the start and end dates cannot exceed 10 years.
    """

    if start_date:
        date_validator(start_date) 
        parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
        valid_start_date = parsed_start.strftime("%d/%m/%Y")
        file_date_suffix = start_date
    else:
        today = date.today()
        valid_start_date = today.strftime("%d/%m/%Y")
        file_date_suffix = today.strftime("%Y-%m-%d")

    if category == "meta":
        url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"
        filename = f"selic_meta_{file_date_suffix}.json"
    else:
        url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
        filename = f"selic_diaria_{file_date_suffix}.json"

    params = {
        "formato": "json",
        "dataInicial": valid_start_date
    }

    if end_date:
        date_validator(end_date)
        parsed_end = datetime.strptime(end_date, "%Y-%m-%d")
        params["dataFinal"] = parsed_end.strftime("%d/%m/%Y")

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
    "fetch_selic"
]