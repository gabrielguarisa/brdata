from brdata.core.crawler import Crawler
import pandas as pd
from brdata.core import exceptions


class XPICrawler(Crawler):
    """Crawler for XP Investimentos.

    Examples:

    ```python
    import brdata
    crawler = brdata.XPICrawler()
    crawler.get_analysis("PETR4")
    ```

    """

    def __init__(self):
        super().__init__("https://conteudos.xpi.com.br/")

    @staticmethod
    def _analysis_page_to_pandas(page) -> pd.Series:
        """Prepara o pd.Series com os dados da ação a partir do conteúdo da página 'content' informado."""
        to_numeric_cols = [
            "Preço Atual",
            "Preço de Entrada",
            "Primeiro Objetivo",
            "Objetivo Final",
            "Stop Loss",
            "Preço Alvo",
            "Potencial",
            "Risco (0 - 100)",
        ]

        product_data = page.find_all("li", {"class": "item-dado-produto"})
        if len(product_data) == 0:
            return None

        data = {}
        for li in product_data:
            spans = li.find_all("span")
            col = spans[0].text

            val = spans[1].text if len(spans) > 1 else li.contents[2]
            val = (
                val.replace("\n", "")
                .replace(",", ".")
                .replace("R$", "")
                .replace("%", "")
                .replace("%", "")
                .split(" ")
            )

            while "" in val:
                val.remove("")

            val = val[0]

            if val == "-":
                val = None
            elif col in to_numeric_cols:
                val = float(val)
            elif col == "Potencial":
                val = float(val) / 100

            data[col] = val

        return pd.Series(data)

    def get_analysis(
        self, code: str, to_pandas: bool = True, enable_cache: bool = True, **kwargs
    ) -> pd.Series:
        """Get stock analysis from XP Investimentos.

        Args:
            code (str): Stock code.
            to_pandas (bool, optional): Whether to return a pandas.Series or a dict. Defaults to True.
            enable_cache (bool, optional): Whether to enable cache. Defaults to True.

        Raises:
            exceptions.NotFoundException: Stock not found.

        Returns:
            pd.Series: Stock analysis.
        """
        try:
            page = super().get_page_soup(
                path=f"/acoes/{code.lower()}", enable_cache=enable_cache, **kwargs
            )
        except exceptions.RequestException as e:
            raise exceptions.NotFoundException(f"[XPI] Stock {code} not found.") from e

        output = self._analysis_page_to_pandas(page)
        if output is None:
            raise exceptions.NotFoundException(f"[XPI] Stock {code} not found.")

        return output if to_pandas else output.to_dict()
