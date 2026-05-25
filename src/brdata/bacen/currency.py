import requests
from datetime import date, datetime
from enum import Enum
from .utils import write_to_disk

class AvailableCurrencies(Enum):
    DKK = "DKK"
    NOK = "NOK"
    SEK = "SEK"
    USD = "USD"
    AUD = "AUD"
    CAD = "CAD"
    EUR = "EUR"
    CHF = "CHF"
    JPY = "JPY"
    GBP = "GBP"

def list_available_currencies():
    """lists available currencies"""
    return [currency.value for currency in AvailableCurrencies]

def currency_price(
        currency: AvailableCurrencies | str,
        price_date: str = None,
        end_price_date: str = None,
        top: int = 100,
        path: str = None
):  
    """
    Returns the daily bulletins with the Bid Parity and Ask Parity, the Bid Quote and Ask Quote for the date or period of the queried currency. It can be downloaded directly if a path is provided.
    \nData Format: MM-DD-YYYY
    """
    currency_code = currency.value.upper() if isinstance(currency, AvailableCurrencies) else str(currency).upper()
    
    try:
        if price_date:
            datetime.strptime(price_date, "%m-%d-%Y")
        if end_price_date:
            datetime.strptime(end_price_date, "%m-%d-%Y")
    except ValueError:
        raise ValueError(
            "The date is in an invalid format. "
            "The correct format must be MM-DD-YYYY (e.g., 12-25-2025)"
        )


    price_date = price_date or date.today().strftime('%m-%d-%Y')

    if not end_price_date:
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='{currency_code}'&@dataCotacao='{price_date}'&$top={top}&$format=json"
        filename = f"{currency_code}_{price_date}.json"
    else:
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='{currency_code}'&@dataInicial='{price_date}'&@dataFinalCotacao='{end_price_date}'&$top={top}&$format=json"
        filename = f"{currency_code}_{price_date}_{end_price_date}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if path:
            write_to_disk(data, filename, path)
        else:
            return data
    
    except Exception as e:
        print(f"Error: {e}")

__all__ = [
    "AvailableCurrencies",
    "currency_price"
]