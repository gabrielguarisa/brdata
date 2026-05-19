import requests
from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from .utils import write_to_disk

class FocusEndpoint(Enum):
    MERCADO_MENSAIS = "ExpectativaMercadoMensais"
    MERCADO_SELIC = "ExpectativasMercadoSelic"
    MERCADO_TRIMESTRAIS = "ExpectativasMercadoTrimestrais"
    MERCADO_ANUAIS = "ExpectativasMercadoAnuais"
    INFLACAO_12M = "ExpectativasMercadoInflacao12Meses"
    INFLACAO_24M = "ExpectativasMercadoInflacao24Meses"
    TOP5_MENSAIS = "ExpectativasMercadoTop5Mensais"
    TOP5_SELIC = "ExpectativasMercadoTop5Selic"
    TOP5_TRIMESTRAIS = "ExpectativaMercadoTop5Trimestral"
    TOP5_ANUAIS = "ExpectativasMercadoTop5Anuais"
    TOP5_INFLACAO_12M = "ExpectativasMercadoTop5Inflacao12Meses"
    TOP5_INFLACAO_24M = "ExpectativasMercadoTop5Inflacao24Meses"
    DATAS_REFERENCIA = "DatasReferencia"

def list_endpoints() -> list[str]:
    """lists available boletim focus endpoints"""
    return [endpoint.value for endpoint in FocusEndpoint]

def fetch_boletim_focus(
        endpoint: FocusEndpoint,
        top: Optional[int] = 100,
        filter_expr: Optional[str] = None,
        path: str = None
) -> Dict[str, Any]:
    """
    Fetches 'Boletim Focus' data. It can be downloaded directly if a file path is provided.
    """
    base_url = f"https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/{endpoint.value}"

    params: Dict[str, Any] = {"$format": "json"}
    if top:
        params["$top"] = top
    if filter_expr:
        params["$filter"] = filter_expr

    try:
        response = requests.get(base_url, params)
        response.raise_for_status()
        data = response.json()
        if path:
            filename = f"boletim_focus_{endpoint}_{date.today()}.json"
            write_to_disk(data, filename, path)
        else:
            return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to query the endpoint {endpoint.name}: {e}")

__all__ = [
    "FocusEndpoint",
    "list_endpoints",
    "fetch_boletim_focus"
]
