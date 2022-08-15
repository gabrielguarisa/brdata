import numpy as np
import pandas as pd

from brdata.utils import get_response


def proventos(
    papel: str,
    group_by_year: bool = False,
    group_by_year_col: str = "Última Data Com",
    provents_type: int = 2,
) -> pd.DataFrame:
    """Histórico de proventos de um fundo imobiliário ou ação.

    Args:
        papel (str): Símbolo do ativo.
        group_by_year (bool, optional): Agrupa os proventos por ano. Defaults to False.
        group_by_year_col (str, optional): Coluna usada para agrupamento por ano. Defaults to "Última Data Com".
        provents_type (int, optional): Tipo de provento. Defaults to 2.

    Returns:
        pd.DataFrame: Histórico de proventos.
    """
    url = f"https://statusinvest.com.br/fii/companytickerprovents?ticker={papel}&chartProventsType={provents_type}"

    r = get_response(url)

    df = pd.DataFrame(r.json()["assetEarningsModels"])

    df["Última Data Com"] = pd.to_datetime(
        df["ed"].replace("-", np.nan), format="%d/%m/%Y"
    )
    df["Data de Pagamento"] = pd.to_datetime(
        df["pd"].replace("-", np.nan), format="%d/%m/%Y"
    )
    df["Valor"] = df["v"]

    if group_by_year:
        return (
            df.groupby(df[group_by_year_col].dt.year)["Valor"]
            .agg(["sum"])
            .rename(columns={"sum": "Valor"})
        )

    return df[["Última Data Com", "Data de Pagamento", "Valor"]]


__all__ = ["proventos"]
