import pandas as pd

from ._base import _Base


class GeralFCA(_Base):
    def __init__(self, folder: str):
        super().__init__(folder, "fca_cia_aberta_geral")

    def get_cia(self, *, cvm_code=None, cnpj=None) -> pd.Series:
        """Retorna os dados de uma cia específica"""
        if cvm_code is None and cnpj is None:
            raise ValueError("Must specify either cvm_code or cnpj")

        code = cvm_code if cvm_code is not None else cnpj
        col = "Codigo_CVM" if cvm_code is not None else "CNPJ_Companhia"

        for year in self.get_years():
            fca = self.get_data(year)
            fca = fca[fca[col] == code]

            if len(fca) > 0:
                return fca.reset_index(drop=True).iloc[0]

        return None

    def get_num_cias_per_year(self) -> pd.Series:
        """Retorna o número de cias por ano"""
        data = {}
        for year in self.get_years():
            data[year] = self.get_data(year)["CNPJ_Companhia"].nunique()

        return pd.Series(data)

    def get_sectors_per_year(self) -> pd.DataFrame:
        """Retorna os setores de atividade por ano"""
        data = {}
        for year in self.get_years():
            data[year] = self.get_data(year)["Setor_Atividade"].value_counts()

        return pd.DataFrame(data)

    def get_most_recent_cias_info(self) -> pd.DataFrame:
        """Retorna os últimos dados encontrados para cada CNPJ"""
        df = pd.concat([self.get_data(year) for year in self.get_years()])
        df.Data_Referencia = pd.to_datetime(df.Data_Referencia)
        return (
            df.sort_values(by=["Data_Referencia", "Versao"])
            .drop_duplicates(subset=["CNPJ_Companhia"], keep="last")
            .reset_index()
        )


class ValorMobiliarioFCA(_Base):
    def __init__(self, folder: str):
        super().__init__(folder, "fca_cia_aberta_valor_mobiliario")

    def get_cia(self, cnpj: str) -> pd.DataFrame:
        """Retorna os dados de valor mobiliário de um determinado CNPJ"""
        for year in self.get_years():
            fca = self.get_data(year)
            fca = fca[fca["CNPJ_Companhia"] == cnpj].dropna(
                subset=["Codigo_Negociacao"]
            )
            if len(fca) > 0:
                return fca.reset_index(drop=True)
        return None

    def get_most_recent_cias_info(
        self, remove_non_active_cias: bool = True
    ) -> pd.DataFrame:
        """Retorna os últimos dados encontrados para cada CNPJ"""
        df = pd.concat([self.get_data(year) for year in self.get_years()])

        df = df.dropna(
            subset=["Data_Referencia", "CNPJ_Companhia", "Codigo_Negociacao"]
        )
        df.Data_Referencia = pd.to_datetime(df.Data_Referencia)
        df = (
            df.sort_values(by=["Data_Referencia", "Versao"])
            .drop_duplicates(subset=["Codigo_Negociacao"], keep="last")
            .reset_index()
        )

        if remove_non_active_cias:
            df = df[df.Data_Fim_Negociacao.isna()]

        return df[
            df["Codigo_Negociacao"].str.contains(
                "^[A-Za-z]+.*[0-9]+$", regex=True, na=False
            )
        ]
