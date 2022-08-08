import shutil
import warnings

import requests
from appdirs import user_cache_dir
from random_user_agent.user_agent import UserAgent
from requests.packages.urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore")

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

__user_agent_rotator = UserAgent()

PKG_NAME = __name__.split(".")[0]
CACHE_DIR: str = user_cache_dir(PKG_NAME)


def new_user_agent() -> str:
    """Retorna um novo User-Agent."""
    return __user_agent_rotator.get_random_user_agent()


def get_response(
    url: str, max_retries: int = 5, timeout: int = 10, verify: bool = True
) -> requests.Response:
    """Retorna uma resposta de uma requisição HTTP.

    Args:
        url (str): url da requisição.
        max_retries (int, optional): número máximo de tentativas. Defaults to 5.
        timeout (int, optional): tempo máximo de espera da requisição. Defaults to 10.
    """
    i = 0
    while True:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": new_user_agent()},
                timeout=timeout,
                verify=verify,
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
            i += 1
            if i >= max_retries:
                break

    raise requests.exceptions.HTTPError("Maximum number of attempts exceeded")


def clear_chache() -> None:
    """Remove qualquer dado no cache."""
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def remove_empty_str(x: str) -> str:
    return next(filter(None, x.split(" ")))
