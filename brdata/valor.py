"""Valor Econômico"""

import datetime
import re

import pandas as pd
from bs4 import BeautifulSoup
from cachier import cachier

from brdata.utils import CACHE_DIR, get_response

BASE_URL = "https://www.valor.com.br/carteira-valor-iframe/historico/{month}/{year}"


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def portfolios(month: int, year: int) -> pd.DataFrame:
    """Portfólios das instituições financeiras.

    Args:
        month (int): Mês.
        year (int): Ano.

    Returns:
        pd.DataFrame: Dataframe com os portfólios das instituições financeiras.
    """
    url = BASE_URL.format(month=month, year=year)
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    tables = soup.find_all(class_="container-corretoras")[0].find_all("table")

    portfolios = {}
    for data in tables:
        name = data.find("th").text
        acoes = [
            re.search("\(([^\)]+)\)", a.text).group()[1:-1]
            for a in data.find("tbody").find_all("tr")
        ]
        portfolios[name] = acoes

    return pd.DataFrame(portfolios)


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def carteira_valor(month: int, year: int) -> pd.DataFrame:
    """Carteira Valor.

    Args:
        month (int): Mês.
        year (int): Ano.

    Returns:
        pd.DataFrame: Dataframe com os dados da carteira valor.
    """
    url = BASE_URL.format(month=month, year=year)
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    table = soup.find_all(class_="bx-tabela-int")[0].find("table")
    df = pd.read_html(str(table), decimal=",", thousands=".")[0].dropna(axis="columns")
    df["Ações"] = df["Ações"].apply(
        lambda x: re.search("\(([^\)]+)\)", x).group()[1:-1]
    )
    return df
