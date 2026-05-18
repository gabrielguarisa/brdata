import os
import json
import requests
from datetime import date

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