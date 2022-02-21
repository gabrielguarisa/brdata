import glob

import pandas as pd


class _Base(object):
    def __init__(self, folder: str, prefix: str):
        folder = f"{folder}/" if folder[-1] != "/" else folder
        self.filenames = glob.glob(f"{folder}{prefix}*")
        self.filenames.sort()
        self.data = {}
        for filename in self.filenames:
            print(filename)
            year = filename.split("_")[-1][:-4]
            self.data[int(year)] = pd.read_csv(filename)

    def get_data(self, year: int) -> pd.DataFrame:
        """Retorna os dados de um ano específico"""
        if year not in self.data:
            raise ValueError(f"Year {year} not found")
        return self.data[year]

    def get_years(self) -> list:
        """Retorna os anos disponíveis"""
        years = list(self.data.keys())
        years.sort(reverse=True)
        return years
