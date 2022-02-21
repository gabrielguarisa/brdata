import pandas as pd

from ._base import _Base


class DistribuicaoCapitalFRE(_Base):
    def __init__(self, folder: str):
        super().__init__(folder, "fre_cia_aberta_distribuicao_capital_2")

    def get_cia(self, cnpj: str) -> pd.DataFrame:
        data = {}

        for year in self.get_years():
            fca = self.get_data(year)
            fca = fca[fca["CNPJ_Companhia"] == cnpj]

            if len(fca) > 0:
                data[year] = (
                    fca.sort_values("Versao", ascending=False)
                    .reset_index(drop=True)
                    .iloc[0]
                )

        return pd.DataFrame(data) if len(data) > 0 else None
