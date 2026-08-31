import io
import pandas as pd
import numpy as np
from playwright.sync_api import sync_playwright
from datetime import date

from .utils import write_to_disk

def crawler_copom_table():
    """Returns the historical interest rate table found on the Central Bank of Brazil's website."""
    with sync_playwright() as p:
        # Crawler
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            "https://www.bcb.gov.br/controleinflacao/historicotaxasjuros"
        )

        page.wait_for_selector("#historicotaxasjuros tbody tr")
        table_html = page.locator("#historicotaxasjuros").evaluate(
            "el => el.outerHTML"
        )
        browser.close()

        # Clean Data
        df = pd.read_html(io.StringIO(table_html))[0]

        df.columns = ['reuniao_num', 'reuniao_data', 'vies', 'vigencia', 'meta_selic', 'tban', 'taxa_selic_pct', 'taxa_selic_aa']
        
        cols_numericas = ['meta_selic', 'taxa_selic_pct', 'taxa_selic_aa']
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce') / 100

        df = df.replace({np.nan: None})

        return df


def fetch_copom_table(
        path: str = None
):
    """
    Fetches historical interest rate table data.
    It can be downloaded directly if a file path is provided.
    """
    df = crawler_copom_table()

    if path:
        dados_json = df.to_dict(orient="records")

        timestamp = date.today()
        filename = f"historico_copom_{timestamp}"

        write_to_disk(dados_json, filename, path)
    else:
        return df

__all__ = [
    "fetch_copom_table"
]
