import typing

from urllib.parse import urljoin

import bs4
from cache_decorator import Cache
from dict_hash import Hashable

from .req import get_response


class Crawler(Hashable):
    def __init__(self, url: str):
        self.url = url

    def join_url(self, *args: str) -> str:
        return urljoin(
            self.url if self.url.endswith("/") else f"{self.url}/", "/".join(args)
        )

    @Cache(
        cache_path="{cache_dir}/{function_name}_{url}_{self.url}.txt",
        validity_duration="1d",
        enable_cache_arg_name="enable_cache",
    )
    def get_page(self, url: str = None, path: str = str, **kwargs) -> str:
        base_url = url if url is not None else self.url

        if path is not None:
            full_url = self.join_url(base_url, path)

        return get_response(full_url, **kwargs).text

    def get_page_soup(
        self, url: str = None, enable_cache: bool = True, **kwargs
    ) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(
            self.get_page(url, enable_cache=enable_cache, **kwargs), "html.parser"
        )

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {"url": self.url}
