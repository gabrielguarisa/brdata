import typing

import pandas as pd


class Processor:
    def __init__(self, **cols) -> None:
        self._cols = cols
        self._data = None

    def set_data(
        self, data: typing.Union[pd.DataFrame, typing.List[pd.DataFrame]]
    ) -> "Processor":
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


class CNPJProcessor(Processor):
    def __init__(
        self,
        cnpj_col: str = "CNPJ_Companhia",
        date_col: str = "Data_Referencia",
        version_col: str = "Versao",
        **cols,
    ):
        super().__init__(cnpj=cnpj_col, date=date_col, version=version_col, **cols)

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


class FCAValorMobiliarioProcessor(CNPJProcessor):
    def __init__(
        self,
        cia_code_col: str = "Codigo_Negociacao",
        end_negotiation_col: str = "Data_Fim_Negociacao",
        **cols,
    ):
        super().__init__(
            cia_code=cia_code_col, end_negotiation=end_negotiation_col, **cols
        )

    def set_data(
        self, data: typing.Union[pd.DataFrame, typing.List[pd.DataFrame]]
    ) -> "FCAValorMobiliarioProcessor":
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


PROCESSORS = {
    "fca": {
        "__default__": CNPJProcessor(),
        "cia_aberta_valor_mobiliario": FCAValorMobiliarioProcessor(),
        "cia_aberta": CNPJProcessor(
            cnpj_col="CNPJ_CIA", date_col="DT_REFER", version_col="VERSAO"
        ),
    },
    "fre": {
        "__default__": CNPJProcessor(),
        "cia_aberta": CNPJProcessor(
            cnpj_col="CNPJ_CIA", date_col="DT_REFER", version_col="VERSAO"
        ),
    },
    "__default__": {"__default__": Processor()},
}


def get_processor(prefix: str, form_name: str) -> Processor:
    processor = PROCESSORS.get(prefix, PROCESSORS["__default__"])

    return processor.get(form_name, processor["__default__"])
