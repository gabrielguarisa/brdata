from typing import Any, Dict

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


def indices(description: bool = True) -> Dict[str, str]:
    if description:
        return INDICES

    return list(INDICES.keys())


def _get_portfolio_data(
    indice: str, segment: bool = False, page_size: int = 100, page_number: int = 1
) -> Dict[str, Any]:
    indice = indice.upper()
    if indice not in indices(False):
        raise ValueError(f"{indice} is not a valid indice")

    payload = {
        "language": "en-us",
        "pageNumber": page_number,
        "pageSize": page_size,
        "index": indice,
        "segment": "2" if segment else "1",
    }
    url = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{}".format(
        base64.b64encode(str(json.dumps(payload)).encode()).decode()
    )

    return get_response(url, verify=False).json()


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def portfolio(indice: str, segment: bool = True) -> pd.DataFrame:
    """Retorna a composição do portfólio do índice."""
    data = _get_portfolio_data(indice, segment)
    data = _get_portfolio_data(indice, segment, page_size=data["page"]["totalRecords"])

    df = pd.DataFrame(data["results"])

    if "theoricalQty" in df.columns:
        df["theoricalQty"] = df["theoricalQty"].str.replace(",", "").astype(float)

    return df
