import requests
from datetime import date, datetime

from .utils import write_to_disk, date_validator

def fetch_ipca(
        start_date: str = None,
        end_date: str = None,
        path: str = None
):
    """ 
    Fetchs IPCA data.
    It can be downloaded directly if a file path is provided.
        
    Date format: str = 'YYYY-MM-DD'
    - The difference between the start and end dates cannot exceed 10 years.
    """

    url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
    
    params = {
        "formato": "json",
    }

    if start_date:
            date_validator(start_date) 
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
             
            params["dataInicial"] = parsed_start.strftime("%d/%m/%Y")
            filename = f"ipca_{start_date}.json"
    else:
        first_event = datetime.strptime("1980-01-01", "%Y-%m-%d").strftime("%Y-%m-%d")
        filename = f"ipca_{first_event}.json"

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
    "fetch_ipca"
]