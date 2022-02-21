from typing import Tuple, Union

import datetime
import io
import os
import zipfile

import pandas as pd
import requests
import xlrd
from cachier import cachier

from .utils import CACHE_DIR, new_user_agent


def _get_new_cookies(count: int = 0, max_retries: int = 5, timeout: int = 5) -> str:
    """Gera novos cookies no site do fundamentus."""
    try:
        req = requests.get(
            "http://fundamentus.com.br/index.php",
            headers={"User-Agent": new_user_agent()},
            timeout=timeout
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
            timeout=timeout
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
