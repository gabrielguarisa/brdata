from brdata.core.crawler import Crawler
from io import BytesIO
from zipfile import ZipFile
import pandas as pd

VALID_PREFIXES = ["DFP", "FCA", "FRE", "IPE", "ITR"]


class CVMCrawler(Crawler):
    """Crawler for CVM data.

    Example:

    ```python
    import brdata
    crawler = brdata.CVMCrawler()
    crawler.get_documents("DFP", 2018, 2020)
    ```

    """

    def __init__(self):
        super().__init__("http://dados.cvm.gov.br/dados/")

    def _get_table_links(
        self, prefix: str, extension: str = ".zip", enable_cache: bool = True
    ):
        if prefix not in VALID_PREFIXES:
            raise ValueError(f"{prefix} is not a valid name")

        page = self.get_page_soup(
            path=f"CIA_ABERTA/DOC/{prefix}/DADOS/", enable_cache=enable_cache
        )
        valid_links = []

        for link_elem in page.find_all("a"):
            link = link_elem.get("href")
            if link[-4:] == extension:
                valid_links.append(link)

        return {zip_url[-8:-4]: zip_url for zip_url in valid_links}

    def get_documents_by_year(self, prefix: str, year: str, enable_cache: bool = True):
        """Get all documents for a given year.

        Args:
            prefix (str): One of the valid prefixes. See `VALID_PREFIXES`.
            year (str): Year to get documents from.
            enable_cache (bool, optional): Whether to use cache or not. Defaults to True.

        Raises:
            ValueError: If prefix is not valid.
            ValueError: If year is not valid.

        Returns:
            dict: Dictionary of pandas.DataFrame with the documents.
        """
        year = str(year)
        prefix = prefix.upper()
        links = self._get_table_links(prefix, enable_cache=enable_cache)

        if year not in links:
            raise ValueError(f"{year} is not a valid year")

        response = self.get_response(
            path=f"CIA_ABERTA/DOC/{prefix}/DADOS/{links[year]}",
            enable_cache=enable_cache,
        )
        all_dfs = {}
        with ZipFile(BytesIO(response.content)) as zip:
            filenames = zip.namelist()

            for filename in filenames:
                if filename.endswith(".csv"):
                    final_name = filename[: -len("_XXXX.csv")]
                    try:
                        df = pd.read_csv(
                            zip.open(filename), delimiter=";", encoding="latin1"
                        )
                        df["year"] = year
                        all_dfs[final_name] = df
                    except Exception as e:
                        print("Invalid file", final_name, e)

        return all_dfs

    def get_documents(
        self, prefix: str, start_year: str, end_year: str, enable_cache: bool = True
    ):
        """Get all documents for a given period.

        Args:
            prefix (str): One of the valid prefixes. See `VALID_PREFIXES`.
            start_year (str): Year to start getting documents from.
            end_year (str): Year to end getting documents from.
            enable_cache (bool, optional): Whether to use cache or not. Defaults to True.

        Raises:
            ValueError: If prefix is not valid.
            ValueError: If start_year is not valid.
            ValueError: If end_year is not valid.

        Returns:
            dict: Dictionary of pandas.DataFrame with the documents.
        """
        all_data = []
        for year in range(int(start_year), int(end_year) + 1):
            all_data.append(
                self.get_documents_by_year(prefix, year, enable_cache=enable_cache)
            )

        output = {}
        for data in all_data:
            for key in data:
                if key not in output:
                    output[key] = data[key]
                else:
                    output[key] = pd.concat([output[key], data[key]])

        return output
