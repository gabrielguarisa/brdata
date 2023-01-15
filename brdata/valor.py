"""Valor Econômico"""

import pandas as pd

from brdata.utils import get_response

MONTH_DICT = {
    "01": "jan",
    "02": "fev",
    "03": "mar",
    "04": "abr",
    "05": "mai",
    "06": "jun",
    "07": "jul",
    "08": "ago",
    "09": "set",
    "10": "out",
    "11": "nov",
    "12": "dez",
}


class ValorEconomico:
    def __init__(self, month: int, year: int, response: dict = None):
        """Valor Econômico

        Parameters
        ----------
        month : int
            Month
        year : int
            Year
        response : dict, optional
            Response, by default None
        """

        if isinstance(month, int):
            month = str(month)

        if isinstance(year, int):
            year = str(year)

        if len(month) == 1:
            month = "0" + month

        self._month = month
        self._year = year
        self._response = response

    @property
    def year(self) -> str:
        return self._year

    @property
    def month(self) -> str:
        return self._month

    @property
    def month_str(self) -> str:
        return MONTH_DICT[self.month]

    @property
    def year_2d(self) -> str:
        return self.year[-2:]

    @property
    def url(self) -> str:
        return f"https://infovalorbucket.s3.amazonaws.com/arquivos/carteira-valor/historico/{self.year}/{self.month}/{self.month_str}{self.year_2d}json.json"

    @property
    def response(self) -> dict:
        if self._response is None:
            response = get_response(self.url, verify=False)
            self._response = response.json()
        return self._response

    def carteira_valor(self) -> pd.DataFrame:
        """Portfólio da Carteira Valor"""
        return pd.DataFrame(self.response["carteiravalor"][0]["indicadas"])

    def carteira_valor_comportamento(self) -> pd.Series:
        """Comportamento da Carteira Valor"""
        return pd.Series(self.response["carteiravalor"][0]["comportamento"][0])

    def carteira_valor_serie_historica(self, ts: str = "12meses") -> pd.DataFrame:
        """Série Histórica da Carteira Valor

        Parameters
        ----------
        ts : str, optional
            Time Series, by default "12meses". Options: "12meses", "2anos", "3anos", "4anos", "5anos"

        Returns
        -------
        pd.DataFrame
            Dataframe with the serie historical
        """
        if ts not in ["12meses", "2anos", "3anos", "4anos", "5anos"]:
            raise ValueError("Invalid ts")

        df_carteiravalor = pd.DataFrame(
            self.response["carteiravalor"][0]["seriehistorica"][0][ts][0]
        )
        df_ibovespa = pd.DataFrame(
            self.response["ibovespa"][0]["seriehistorica"][0][ts][0]
        )
        df = pd.merge(
            df_carteiravalor,
            df_ibovespa,
            on="datas",
            suffixes=("_carteiravalor", "_ibovespa"),
        )
        df = df.rename(
            columns={
                "valores_carteiravalor": "carteiravalor",
                "valores_ibovespa": "ibovespa",
            }
        )
        return df

    def corretoras(self) -> pd.DataFrame:
        """Portfólio das Corretoras da Carteira Valor"""
        dfs = []
        for i in range(len(self.response["corretoras"])):
            df = pd.DataFrame(
                self.response["corretoras"][i]["corretora"][0]["indicadas"]
            )
            df["nome"] = self.response["corretoras"][i]["corretora"][0]["nome"]
            dfs.append(df)

        return pd.concat(dfs).reset_index(drop=True)

    def corretoras_comportamento(self) -> pd.DataFrame:
        """Comportamento das Corretoras da Carteira Valor"""
        df = []
        for i in range(len(self.response["corretoras"])):
            data = self.response["corretoras"][i]["corretora"][0]["comportamento"][0]
            data["nome"] = self.response["corretoras"][i]["corretora"][0]["nome"]
            data["entram"] = self.response["corretoras"][i]["corretora"][0][
                "alteracoes"
            ][0]["entram"].split(", ")
            data["saem"] = self.response["corretoras"][i]["corretora"][0]["alteracoes"][
                0
            ]["saem"].split(", ")
            data["nota"] = self.response["corretoras"][i]["corretora"][0]["nota"]
            df.append(data)

        return pd.DataFrame(df)

    def corretoras_serie_historica(self, ts: str = "12meses") -> pd.DataFrame:
        """Série Histórica das Corretoras da Carteira Valor

        Parameters
        ----------
        ts : str, optional
            Time Series, by default "12meses". Options: "12meses", "2anos", "3anos", "4anos", "5anos"

        Returns
        -------
        pd.DataFrame
            Dataframe with the serie historical
        """
        if ts not in ["12meses", "2anos", "3anos", "4anos", "5anos"]:
            raise ValueError("Invalid ts")

        dfs = []
        for i in range(len(self.response["corretoras"])):
            dfs.append(
                pd.DataFrame(
                    self.response["corretoras"][i]["corretora"][0]["seriehistorica"][0][
                        ts
                    ]
                )
            )
            dfs[i] = dfs[i].set_index(["datas"])
            dfs[i] = dfs[i].rename(
                columns={
                    "valores": self.response["corretoras"][i]["corretora"][0]["nome"]
                }
            )

        return pd.concat(dfs, axis=1).reset_index()


__all__ = ["ValorEconomico"]
