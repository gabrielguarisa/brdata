import requests
from urllib.parse import quote, urlencode

from .utils import write_to_disk, date_validator

class BoletimFocus:
    """
    It provides access to market expectations for economic indicators such as IPCA, Selic, exchange rate, and GDP. 
    It can be downloaded directly if a path is provided.
    """
    def __init__(self):
        self.base_url = (
            "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        )
    
    def _get(
            self,
            endpoint: str,
            indicador: str = None,
            start_date: str = None,
            end_date: str = None,
            top: int = 100,
            path: str = None,
    ):
        url = f"{self.base_url}/{endpoint}"

        filter = []
        if indicador: 
            filter.append(f"Indicador eq '{indicador}'")
        if start_date:
            valid_start_date = date_validator(start_date)
            filter.append(f"Data ge '{valid_start_date}'")
        if end_date:
            valid_end_date = date_validator(end_date)
            filter.append(f"Data le '{valid_end_date}'")
        
        params = {"$top": top, "$format": "json"}

        if filter:
            params["$filter"] = " and ".join(filter)
        
        params_encoded = urlencode(params, quote_via=quote, safe="()'")
        url_completa = f"{url}?{params_encoded}"

        response = requests.get(url_completa)
        response.raise_for_status()

        data = response.json().get("value", [])
        filename = f"{endpoint}.json"

        if path:
            write_to_disk(data, filename, path)
        
        return data

    # --- ENDPOINTS ---

    def expectativas_mensais(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativaMercadoMensais"""
        return self._get("ExpectativaMercadoMensais", indicador, start_date, end_date, top, path)
    
    def expectativas_selic(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoSelic"""
        return self._get("ExpectativasMercadoSelic", indicador, start_date, end_date, top, path)
    
    def expectativas_trimestrais(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTrimestrais"""
        return self._get("ExpectativasMercadoTrimestrais", indicador, start_date, end_date, top, path)
    
    def expectativas_anuais(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoAnuais"""
        return self._get("ExpectativasMercadoAnuais", indicador, start_date, end_date, top, path)
    
    def inflacao_12meses(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoInflacao12Meses"""
        return self._get("ExpectativasMercadoInflacao12Meses", indicador, start_date, end_date, top, path)
    
    def inflacao_24meses(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoInflacao24Meses"""
        return self._get("ExpectativasMercadoInflacao24Meses", indicador, start_date, end_date, top, path)
    
    def top5_mensais(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTop5Mensais"""
        return self._get("ExpectativasMercadoTop5Mensais", indicador, start_date, end_date, top, path)
    
    def top5_selic(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTop5Selic"""
        return self._get("ExpectativasMercadoTop5Selic", indicador, start_date, end_date, top, path)
    
    def top5_trimestral(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativaMercadoTop5Trimestral"""
        return self._get("ExpectativaMercadoTop5Trimestral", indicador, start_date, end_date, top, path)
    
    def top5_anuais(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTop5Anuais"""
        return self._get("ExpectativasMercadoTop5Anuais", indicador, start_date, end_date, top, path)
    
    def top5_inflacao_12meses(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTop5Inflacao12Meses"""
        return self._get("ExpectativasMercadoTop5Inflacao12Meses", indicador, start_date, end_date, top, path)
    
    def top5_inflacao_24meses(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: ExpectativasMercadoTop5Inflacao24Meses"""
        return self._get("ExpectativasMercadoTop5Inflacao24Meses", indicador, start_date, end_date, top, path)
    
    def datas_referencia(
            self, 
            indicador: str = None, 
            start_date: str = None, 
            end_date: str = None, 
            top: int = 100, 
            path: str = None
            ):
        """Endpoint: DatasReferencia"""
        return self._get("DatasReferencia", indicador, start_date, end_date, top, path)
    
__all__ = [
    "BoletimFocus"
]
