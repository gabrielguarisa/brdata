import pandas as pd

from brdata.utils import get_response


def fii_proventos(
    papel: str,
    group_by_year: bool = False,
    group_by_year_col: str = "Última Data Com",
    provents_type: int = 2,
):
    url = f"https://statusinvest.com.br/fii/companytickerprovents?ticker={papel}&chartProventsType={provents_type}"

    r = get_response(url)

    df = pd.DataFrame(r.json()["assetEarningsModels"])

    df["Última Data Com"] = pd.to_datetime(df["ed"], format="%d/%m/%Y")
    df["Data de Pagamento"] = pd.to_datetime(df["pd"], format="%d/%m/%Y")
    df["Valor"] = df["v"]

    if group_by_year:
        return (
            df.groupby(df[group_by_year_col].dt.year)["Valor"]
            .agg(["sum"])
            .rename(columns={"sum": "Valor"})
        )

    return df[["Última Data Com", "Data de Pagamento", "Valor"]]
