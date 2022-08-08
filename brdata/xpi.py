import datetime

import pandas as pd
from bs4 import BeautifulSoup
from cachier import cachier

from .utils import CACHE_DIR, get_response


def _get_dados_produto(content: bytes) -> pd.Series:
    """Prepara o pd.Series com os dados da ação a partir do conteúdo da página 'content' informado."""
    to_numeric_cols = [
        "Preço Atual",
        "Preço de Entrada",
        "Primeiro Objetivo",
        "Objetivo Final",
        "Stop Loss",
        "Preço Alvo",
        "Potencial",
        "Risco (0 - 100)",
    ]
    soup = BeautifulSoup(content, "html.parser")

    dados_produto = soup.find_all("li", {"class": "item-dado-produto"})
    if len(dados_produto) == 0:
        return None

    data = {}
    for li in dados_produto:
        spans = li.find_all("span")
        col = spans[0].text

        val = spans[1].text if len(spans) > 1 else li.contents[2]
        val = (
            val.replace("\n", "")
            .replace(",", ".")
            .replace("R$", "")
            .replace("%", "")
            .replace("%", "")
            .split(" ")
        )

        while "" in val:
            val.remove("")

        val = val[0]

        if val == "-":
            val = None
        elif col in to_numeric_cols:
            val = float(val)
        elif col == "Potencial":
            val = float(val) / 100

        data[col] = val

    return pd.Series(data)


@cachier(stale_after=datetime.timedelta(hours=1), cache_dir=CACHE_DIR)
def analise(papel: str, tecnica: bool = False) -> pd.Series:
    """Retorna os dados da análise de uma ação definida em 'papel'.
    Args:
        papel (str): Código da ação.
        tecnica (bool, optional): Retorna a análise técnica da ação. O valor padrão é False.
    Returns:
        pd.Series: Dados da análise.
    """
    url = f"https://conteudos.xpi.com.br/acoes/{papel.lower()}{'/analise-tecnica/' if tecnica else '/'}"
    response = get_response(url)
    return _get_dados_produto(response.content)


__all__ = ["analise"]
