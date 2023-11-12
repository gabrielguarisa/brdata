from urllib.parse import urljoin

import bs4
from dict_hash import Hashable

from .req import get_response
import requests


class Crawler(Hashable):
    """Base class for crawlers.

    If you want to create a new crawler, you should inherit from this class.
    It provides some useful methods for crawling.

    Args:
        url (str): Base url for the crawler.
    """

    def __init__(self, url: str):
        self.url = url

    def join_url(self, *args: str) -> str:
        """Join url parts.

        Args:
            *args (str): Url parts.

        Returns:
            str: Joined url.
        """
        return urljoin(
            self.url if self.url.endswith("/") else f"{self.url}/", "/".join(args)
        )

    def get_response(
        self, url: str = None, path: str = str, **kwargs
    ) -> requests.Response:
        """Get a response from a given url.

        Args:
            url (str, optional): Url to get response from. Defaults to None.
            path (str, optional): Path to join with base url. Defaults to str.
            kwargs: Keyword arguments to pass to `requests.get`.

        Returns:
            requests.Response: Response from the given url.
        """
        base_url = url if url is not None else self.url

        if path is not None:
            full_url = self.join_url(base_url, path)

        return get_response(full_url, **kwargs)

    def get_page(self, url: str = None, path: str = str, **kwargs) -> str:
        """Get a page from a given url. This is just a wrapper around `get_response` method."""
        return self.get_response(url, path, **kwargs).text

    def get_page_soup(
        self, url: str = None, enable_cache: bool = True, **kwargs
    ) -> bs4.BeautifulSoup:
        """Get a BeautifulSoup object from a given url. This is just a wrapper around `get_page` method."""
        return bs4.BeautifulSoup(
            self.get_page(url, enable_cache=enable_cache, **kwargs), "html.parser"
        )
