from io import StringIO
import typing
import bs4
import pandas as pd
from brdata.core.crawler import Crawler
from brdata.core import exceptions


class ValorEconomicoCrawler(Crawler):
    """Crawler for Valor Economico.

    Examples:

    ```python
    import brdata
    crawler = brdata.ValorEconomicoCrawler()
    crawler.get_recommended_wallet_by_month(1, 2022)
    ```

    """

    def __init__(self):
        super().__init__(
            "https://infograficos.valor.globo.com/carteira-valor/historico"
        )

    def get_page_soup(
        self, month: int, year: int, enable_cache: bool = True, **kwargs
    ) -> bs4.BeautifulSoup:
        page = super().get_page_soup(
            path=f"/{month}/{year}", enable_cache=enable_cache, **kwargs
        )
        element = page.find("a", {"id": "datepicker-historico"})

        if not element:
            raise exceptions.NotFoundException("[ValorEconomico] No datepicker found.")

        if element["data-mes"] != str(month) or element["data-ano"] != str(year):
            raise exceptions.NotFoundException(
                f"[ValorEconomico] No data found for the given month and year: {month}/{year}"
            )
        return page

    @staticmethod
    def _format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df.rename(
            columns={
                "Nome  Nome/Código": "name",
                "Código": "code",
                "Indicações": "recommendations",
                "Variação no mês  Var. Mês": "month_variation",
                "Variação no mês": "month_variation",
            },
            inplace=True,
        )

        df["month_variation"] = (
            df["month_variation"]
            .str.replace("%", "")
            .str.replace(",", ".")
            .astype(float)
            / 100
        )
        return df

    @staticmethod
    def _format_table(table) -> pd.DataFrame:
        df = pd.read_html(StringIO(table.prettify()))[0]

        return ValorEconomicoCrawler._format_dataframe(df)

    def get_recommended_wallet_by_month(
        self, month: int, year: int, to_pandas: bool = True, enable_cache: bool = True
    ) -> pd.DataFrame:
        """Get recommended wallet for a given month and year.

        Args:
            month (int): Month.
            year (int): Year.
            to_pandas (bool, optional): If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True.
            enable_cache (bool, optional): If True, enables cache. Defaults to True.

        Returns:
            pd.DataFrame: Recommended wallet for a given month and year.
        """
        table = (
            self.get_page_soup(month=month, year=year, enable_cache=enable_cache)
            .find("div", {"class": "indicadas"})
            .find("table")
        )
        table.find("tfoot").clear()

        try:
            output = ValorEconomicoCrawler._format_table(table)
            output["month"] = month
            output["year"] = year
            return output if to_pandas else output.to_dict("records")
        except Exception as e:
            raise exceptions.NotFoundException(
                f"[ValorEconomico] No table found for the given month and year: {month}/{year}"
            ) from e

    def get_wallets_from_institutions_by_month(
        self, month: int, year: int, to_pandas: bool = True, enable_cache: bool = True
    ) -> pd.DataFrame:
        """Get wallets from institutions for a given month and year.

        Args:
            month (int): Month.
            year (int): Year.
            to_pandas (bool, optional): If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True.
            enable_cache (bool, optional): If True, enables cache. Defaults to True.

        Returns:
            pd.DataFrame: Wallets from institutions for a given month and year.
        """
        page = self.get_page_soup(month=month, year=year, enable_cache=enable_cache)

        container = page.find("div", {"class": "bx-container corretoras"})

        names = [title.text for title in container.find_all("p", {"class": "titulo"})]
        tables = [
            ValorEconomicoCrawler._format_table(t.find("table"))
            for t in container.find_all("div", {"class": "tabela"})
        ]

        output = []
        for i in range(len(names)):
            tables[i]["institution"] = names[i]
            tables[i]["month"] = month
            tables[i]["year"] = year
            output.append(tables[i])

        output = pd.concat(output)

        return output if to_pandas else output.to_dict("records")

    @staticmethod
    def _execute_in_range(
        start_date: str,
        end_date: str,
        func: typing.Callable,
        to_pandas: bool = True,
        enable_cache: bool = True,
    ):
        start_date = pd.to_datetime(start_date, format="ISO8601")
        end_date = pd.to_datetime(end_date, format="ISO8601")

        output = []
        while start_date <= end_date:
            output.append(
                func(start_date.month, start_date.year, enable_cache=enable_cache)
            )
            start_date = start_date + pd.DateOffset(months=1)

        output = pd.concat(output).reset_index(drop=True)
        return output if to_pandas else output.to_dict("records")

    def get_recommended_wallet(
        self,
        start_date: str,
        end_date: str,
        to_pandas: bool = True,
        enable_cache: bool = True,
    ):
        """Get recommended wallet.

        Args:
            start_date (str): Start date in ISO8601 format.
            end_date (str): End date in ISO8601 format.
            to_pandas (bool, optional): If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True.
            enable_cache (bool, optional): If True, enables cache. Defaults to True.

        Returns:
            pd.DataFrame: History of recommended wallet.
        """
        return self._execute_in_range(
            start_date,
            end_date,
            self.get_recommended_wallet_by_month,
            to_pandas=to_pandas,
            enable_cache=enable_cache,
        )

    def get_wallets_from_institutions(
        self,
        start_date: str,
        end_date: str,
        to_pandas: bool = True,
        enable_cache: bool = True,
    ):
        """Get wallets from institutions.

        Args:
            start_date (str): Start date in ISO8601 format.
            end_date (str): End date in ISO8601 format.
            to_pandas (bool, optional): If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True.
            enable_cache (bool, optional): If True, enables cache. Defaults to True.

        Returns:
            pd.DataFrame: History of wallets from institutions.
        """

        return self._execute_in_range(
            start_date,
            end_date,
            self.get_wallets_from_institutions_by_month,
            to_pandas=to_pandas,
            enable_cache=enable_cache,
        )
