from typing import Tuple, Union

import datetime
import io
import os
import zipfile

import numpy as np
import pandas as pd
import requests
import xlrd
from bs4 import BeautifulSoup
from cachier import cachier

from brdata.utils import CACHE_DIR, get_response, new_user_agent


def _get_new_cookies(count: int = 0, max_retries: int = 5, timeout: int = 5) -> str:
    """Gera novos cookies no site do fundamentus."""
    try:
        req = requests.get(
            "http://fundamentus.com.br/index.php",
            headers={"User-Agent": new_user_agent()},
            timeout=timeout,
        )

        return req.cookies["PHPSESSID"]
    except Exception:
        while count < max_retries:
            return _get_new_cookies(count + 1, max_retries)

        return ""


def _set_cookies_balanco_historico(papel: str, cookie: str, timeout: int = 5):
    """Esta função atrela um cookie a uma determinada ação."""
    headers = {
        "User-Agent": new_user_agent(),
        "Cookie": f"PHPSESSID={cookie}",
        "Referer": f"http://fundamentus.com.br/detalhes.php?papel={papel}",
    }
    try:
        requests.get(
            f"http://fundamentus.com.br/balancos.php?papel={papel}&tipo=1",
            headers=headers,
            timeout=timeout,
        )
    except Exception:
        raise Exception("Error in requests [Set cookies]")


def ler_balanco(filename: Union[str, bytes]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Conversão das planilhas de balanço histórico para dataframes.
    Args:
        filename (str): Nome do arquivo.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Dataframes de Balanço patrimonial e Demonstrativo de resultados.
    """
    if isinstance(filename, str):
        rb = xlrd.open_workbook(filename, logfile=open(os.devnull, "w"))
    else:
        rb = xlrd.open_workbook(file_contents=filename, logfile=open(os.devnull, "w"))
    balanco, demonstrativo = pd.read_excel(
        rb, skiprows=1, sheet_name=[0, 1], index_col=0
    ).values()

    balanco = balanco.T
    balanco.index = pd.to_datetime(balanco.index)

    demonstrativo = demonstrativo.T
    demonstrativo.index = pd.to_datetime(demonstrativo.index)

    return balanco, demonstrativo


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def balanco_historico(papel: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Balanços históricos do papel informado.
    Args:
        papel (str): Símbolo do ativo.
    Raises:
        ValueError: Caso ocorra algum erro na requisição.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Balanço patrimonial e Demonstrativos de resultados.
    """
    cookie = _get_new_cookies()

    if cookie:
        _set_cookies_balanco_historico(papel, cookie)

        r = requests.get(
            f"http://fundamentus.com.br/planilhas.php?SID={cookie}",
            headers={"User-Agent": new_user_agent()},
            stream=True,
        )
    else:
        raise ValueError(f"Invalid cookie for {papel}")

    z = zipfile.ZipFile(io.BytesIO(r.content))
    sheet = z.read(z.infolist()[0])
    z.close()
    return ler_balanco(sheet)


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def resultados(fii: bool = False) -> pd.DataFrame:
    """Retorna os dados de todos os ativos disponíveis no fundamentus.
    Args:
        fii (bool, optional): Retorna os dados dos FIIs ao invés das ações. Valor padrão é False.
    Returns:
        pd.DataFrame: Dados dos ativos.
    """
    replace_cols = (
        ["FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média"]
        if fii
        else [
            "Div.Yield",
            "Mrg Ebit",
            "Mrg. Líq.",
            "ROIC",
            "ROE",
            "Cresc. Rec.5a",
        ]
    )
    url = f"https://www.fundamentus.com.br/{'fii_' if fii else ''}resultado.php"

    r = requests.get(url, headers={"User-Agent": new_user_agent()})
    df = pd.read_html(r.text, decimal=",", thousands=".", index_col=0)[0]

    for c in replace_cols:
        df[c] = df[c].apply(lambda x: x.replace(".", "").replace(",", ".").rstrip("%"))
        df[c] = pd.to_numeric(df[c]) / 100.00

    return df


def _get_detalhes_tables(symbol):
    url = f"http://www.fundamentus.com.br/detalhes.php?papel={symbol.lower()}"
    r = get_response(url)

    soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")
    tables = soup.findAll("table")

    return pd.read_html(str(tables).replace("?", ""), decimal=",", thousands=".")


def _table_without_header(table):
    data = {}

    for row in table.iterrows():
        data[row[1][0]] = row[1][1]
        data[row[1][2]] = row[1][3]

    data = pd.Series(data)

    for col in ["Últ balanço processado", "Data últ cot"]:
        if col in data:
            data[col] = pd.to_datetime(data[col])

    data.replace("-", np.nan, inplace=True)
    return data


def _table_with_single_header(table):
    cols = table.iloc[0]
    data = {col: {} for col in cols.unique()}

    for row in table.iloc[1:].iterrows():
        for i in range(0, len(cols), 2):
            value = row[1][i + 1]
            if isinstance(value, str) and value.endswith("%"):
                value = value.replace("%", "")
                value = value.replace(",", ".")
                value = float(value) / 100

            data[cols[i]][row[1][i]] = value

    return {col: pd.Series(data[col]).dropna().replace("-", np.nan) for col in data}


def _table_with_double_header(table):
    cols = table.iloc[0]
    data = {}

    for col in cols.unique():
        valid_table = table.iloc[1:, [i for i, c in enumerate(cols) if c == col]]
        data[col] = pd.DataFrame(_table_with_single_header(valid_table))

    return data


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def detalhes(symbol):
    tables = _get_detalhes_tables(symbol)

    results = {}

    results["Metadata"] = pd.concat(
        [_table_without_header(tables[0]), _table_without_header(tables[1])], axis=0
    )

    results = {
        **results,
        **_table_with_single_header(tables[2]),
        **_table_with_single_header(tables[3]),
    }

    results = {**results, **_table_with_double_header(tables[4])}

    return results
