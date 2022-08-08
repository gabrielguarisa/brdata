from typing import Any, Dict, List, Union

import base64
import datetime
import json

import pandas as pd
import urllib3
from cachier import cachier

from brdata.utils import get_response

from .utils import CACHE_DIR

urllib3.disable_warnings()

INDICES = {
    "IBOV": "Índice Bovespa - É o principal indicador de desempenho das ações negociadas na B3 e reúne as empresas mais importantes do mercado de capitais brasileiro",
    "IBXX": "Índice IBrX 100 - 100 ativos de maior negociabilidade e representatividade do mercado de ações brasileiro.",
    "IBXL": "Índice IBrX 50 - 50 ativos de maior negociabilidade e representatividade do mercado de ações brasileiro.",
    "IBRA": "Índice Brasil Amplo - O objetivo do IBrA é ser o indicador do desempenho médio das cotações de todos os ativos negociados no mercado a vista (lote-padrão) da B3 que atendam a critérios mínimos de liquidez e presença em pregão, de forma a oferecer uma visão ampla do mercado acionário.",
    "IFNC": "Índice Financeiro - ativos de maior negociabilidade e representatividade dos setores de intermediários financeiros, serviços financeiros diversos, previdência e seguros.",
    "ICON": "Índice de Consumo - ativos de maior negociabilidade e representatividade dos setores de consumo cíclico, consumo não cíclico e saúde.",
    "IEEX": "Índice de Energia Elétrica - ativos de maior negociabilidade e representatividade do setor de energia elétrica.",
    "IFIX": "Índice de Fundos Imobiliários - Fundos imobiliários negociados nos mercados de bolsa e de balcão organizado da B3.",
    "IFIL": "Índice de Fundos Imobiliários de Alta Liquidez - Fundos imobiliários mais líquidos negociados nos mercados de bolsa e de balcão organizado da B3.",
    "IMAT": "Índice de Materiais Básicos - ativos de maior negociabilidade e representatividade do setor de materiais básicos.",
    "IDIV": "Índice Dividendos - ativos que se destacaram em termos de remuneração dos investidores, sob a forma de dividendos e juros sobre o capital próprio.",
    "INDX": "Índice do Setor Industrial - ativos de maior negociabilidade e representatividade dos setores da atividade industrial compreendidos por materiais básicos, bens industriais, consumo cíclico, consumo não cíclico, tecnologia da informação e saúde.",
    "IMOB": "Índice Imobiliário - ativos de maior negociabilidade e representatividade dos setores da atividade imobiliária compreendidos por exploração de imóveis e construção civil.",
    "MLCX": "Índice MidLarge Cap - ativos de uma carteira composta pelas empresas de maior capitalização.",
    "SMLL": "Índice Small Cap - empresas de menor capitalização.",
    "UTIL": "Índice Utilidade Pública - ativos de maior negociabilidade e representatividade do setor de utilidade pública (energia elétrica, água e saneamento e gás).",
    "IVBX": "Índice Valor empresas bem conceituadas pelos investidores.",
}

BASE_API_URL = "https://sistemaswebb3-listados.b3.com.br"


def indices(description: bool = True) -> Union[Dict[str, str], List[str]]:
    """Lista de índices válidos.

    Args:
        description (bool, optional): Retorna a descrição do índice. Defaults to True.

    Returns:
        Union[Dict[str, str], List[str]]: Lista de índices válidos.
    """
    if description:
        return INDICES

    return list(INDICES.keys())


def _payload_to_base64(payload: Dict[str, Any]) -> str:
    return base64.b64encode(str(json.dumps(payload)).encode()).decode()


def _get_api_data(path_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = "{}{}{}".format(BASE_API_URL, path_url, _payload_to_base64(payload))

    return get_response(url, verify=False).json()


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def portfolio(indice: str, segment: bool = True) -> pd.DataFrame:
    """Retorna a composição do portfólio do índice.

    Args:
        indice (str): Nome do índice. Use a função `b3.indices()`.
        segment (bool, optional): Indica se os segmentos serão retornados. Defaults to True.

    Raises:
        ValueError: Retornado caso não esteja na lista de índices válidos.

    Returns:
        pd.DataFrame: Lista de ativos que estão no índice.
    """
    indice = indice.upper()
    if indice not in indices(False):
        raise ValueError(f"{indice} is not a valid indice")

    payload = {
        "language": "en-us",
        "pageNumber": 1,
        "pageSize": 100,
        "index": indice,
        "segment": "2" if segment else "1",
    }
    data = _get_api_data("/indexProxy/indexCall/GetPortfolioDay/", payload)
    payload["pageSize"] = data["page"]["totalRecords"]
    data = _get_api_data("/indexProxy/indexCall/GetPortfolioDay/", payload)

    df = pd.DataFrame(data["results"])

    if "theoricalQty" in df.columns:
        df["theoricalQty"] = df["theoricalQty"].str.replace(",", "").astype(float)

    return df


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def cias() -> pd.DataFrame:
    """Retorna todas as empresas listadas na B3."""
    payload = {"language": "en-us", "pageNumber": 1, "pageSize": 100}
    data = _get_api_data(
        "/listedCompaniesProxy/CompanyCall/GetInitialCompanies/", payload
    )
    payload["pageSize"] = data["page"]["totalRecords"]
    data = _get_api_data(
        "/listedCompaniesProxy/CompanyCall/GetInitialCompanies/", payload
    )

    df = pd.DataFrame(data["results"])

    return df


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def bdrs() -> pd.DataFrame:
    """Retorna todas as BDRs listadas na B3."""
    payload = {"language": "en-us", "pageNumber": 1, "pageSize": 100}
    data = _get_api_data("/listedCompaniesProxy/CompanyCall/GetCompaniesBDR/", payload)
    payload["pageSize"] = data["page"]["totalRecords"]
    data = _get_api_data("/listedCompaniesProxy/CompanyCall/GetCompaniesBDR/", payload)

    df = pd.DataFrame(data["results"])

    return df


@cachier(stale_after=datetime.timedelta(days=7), cache_dir=CACHE_DIR)
def detalhes(cvm_code: str) -> pd.Series:
    """Retorna as informações detalhadas de uma empresa."""
    payload = {"language": "en-us", "codeCVM": cvm_code}
    data = _get_api_data("/listedCompaniesProxy/CompanyCall/GetDetail/", payload)

    return pd.Series(data)


__all__ = ["indices", "portfolio", "cias", "bdrs", "detalhes"]
