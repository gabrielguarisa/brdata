from typing import Optional, Union

from .copom import fetch_copom_table
from .currency import AvailableCurrencies, currency_price
from .selic import fetch_selic


class BCBClient:
    """
    It provides access to quotes and Central Bank information, such as the Selic rate, market rates, the IPCA, and the COPOM calendar.
    It can be downloaded directly if a path is provided.
    """
    def __init__(self, default_save_path: Optional[str] = None):
        self.default_save_path = default_save_path

    def get_copom_calendar(self, path: Optional[str] = None):
        target_path = path or self.default_save_path
        return fetch_copom_table(path = target_path)

    def get_currencies(
        self,
        currency: Union[AvailableCurrencies, str],
        price_date: Optional[str] = None,
        end_price_date: Optional[str] = None,
        top: int = 100,
        path: Optional[str] = None
    ):
        target_path = path or self.default_save_path
        return currency_price(
            currency = currency,
            price_date = price_date,
            end_price_date = end_price_date,
            top = top,
            path = target_path
        )

    def get_selic_meta(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        path: Optional[str] = None,
    ):
        target_path = path or self.default_save_path
        return fetch_selic(
            category = "meta",
            start_date = start_date,
            end_date = end_date,
            path = target_path
        )

    def get_selic_diaria(
            self,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            path: Optional[str] = None,
        ):
            target_path = path or self.default_save_path
            return fetch_selic(
                category = "diaria",
                start_date = start_date,
                end_date = end_date,
                path = target_path
            )
