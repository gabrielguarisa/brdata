import typing

import pandas as pd

from .download import get_data


class FCAProcessor:
    def __init__(
        self,
        cnpj_col: str = "CNPJ_Companhia",
        date_col: str = "Data_Referencia",
        version_col: str = "Versao",
    ):
        self._data = None

        self._cols = {"cnpj": cnpj_col, "date": date_col, "version": version_col}

    def set_data(
        self, data: typing.Union[pd.DataFrame, typing.List[pd.DataFrame]]
    ) -> "FCAProcessor":
        """Seta os dados"""
        if isinstance(data, pd.DataFrame):
            data = [data]

        self._data = pd.concat(data).reset_index(drop=True)

        for col in self._cols.values():
            if col not in self._data.columns:
                raise ValueError(f"{col} not in data columns")

        return self

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def get_most_recent(self) -> pd.DataFrame:
        """Retorna os últimos dados encontrados para cada CNPJ"""
        df = (
            self.data.sort_values(by=[self._cols["date"], self._cols["version"]])
            .drop_duplicates(subset=[self._cols["cia_code"]], keep="last")
            .reset_index(drop=True)
        )

        return df.reset_index(drop=True)

    def get_cia_history(self, cnpj: str) -> pd.DataFrame:
        """Retorna os dados de valor mobiliário de um determinado CNPJ"""
        return self.data[self.data[self._cols["cnpj"]] == cnpj].reset_index(drop=True)


class ValorMobiliarioProcessor(FCAProcessor):
    def __init__(
        self,
        cia_code_col: str = "Codigo_Negociacao",
        end_negotiation_col: str = "Data_Fim_Negociacao",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._cols["cia_code"] = cia_code_col
        self._cols["end_negotiation"] = end_negotiation_col

    def set_data(
        self, data: typing.Union[pd.DataFrame, typing.List[pd.DataFrame]]
    ) -> "ValorMobiliarioProcessor":
        super().set_data(data)

        self._data = self._data.dropna(
            subset=[self._cols["date"], self._cols["cnpj"], self._cols["cia_code"]]
        )
        self._data[self._cols["date"]] = pd.to_datetime(self._data[self._cols["date"]])

        self._data = self._data[
            self._data[self._cols["cia_code"]].str.contains(
                "^[A-Za-z]+.*[0-9]+$", regex=True, na=False
            )
        ]
        self._data = self.data.reset_index(drop=True)

        return self

    def get_most_recent(self, remove_non_active: bool = True) -> pd.DataFrame:
        """Retorna os últimos dados encontrados para cada CNPJ"""
        df = super().get_most_recent()

        if remove_non_active:
            df = df[df[self._cols["end_negotiation"]].isna()].reset_index(drop=True)

        return df


PROCESSOR_BY_PREFIX = {
    "fca_cia_aberta_valor_mobiliario": ValorMobiliarioProcessor(),
    "fca_cia_aberta": FCAProcessor(
        cnpj_col="CNPJ_CIA", date_col="DT_REFER", version_col="VERSAO"
    ),
}


class FCAReader:
    def __init__(self, data: typing.Dict[str, pd.DataFrame] = get_data("fca")) -> None:
        _dfs = {}
        self._processors = {}
        self._years = []

        for filename in list(data.keys()):
            prefix = filename[:-5]
            year = int(filename[-4:])

            if year not in self._years:
                self._years.append(year)

            if prefix not in _dfs:
                _dfs[prefix] = []

            _dfs[prefix].append(data[filename])

        for prefix, group in _dfs.items():
            self._processors[prefix] = PROCESSOR_BY_PREFIX.get(
                prefix, FCAProcessor()
            ).set_data(group)

        self._years.sort()

    @property
    def processors(self) -> typing.Dict[str, FCAProcessor]:
        return self._processors

    @property
    def years(self) -> typing.List[int]:
        return self._years

    @property
    def prefixes(self) -> typing.List[str]:
        return list(self._processors.keys())

    def get_data(self, prefix: str) -> pd.DataFrame:
        if prefix not in self.processors:
            raise ValueError(
                f"Prefix {prefix} not found. Available prefixes: {self.prefixes}"
            )

        return self.processors[prefix].data
