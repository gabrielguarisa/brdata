import requests
from random_user_agent.user_agent import UserAgent
from brdata.core import exceptions
from cache_decorator import Cache

user_agent_rotator = UserAgent()


def new_user_agent() -> str:
    """Returns a new random user agent."""
    return user_agent_rotator.get_random_user_agent()


@Cache(
    validity_duration="1d",
    enable_cache_arg_name="enable_cache",
)
def get_response(
    url: str, max_retries: int = 5, timeout: int = 10, verify: bool = True
) -> requests.Response:
    """Returns a response from a given url.

    Args:
        url (str): url to get response from.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        timeout (int, optional): Timeout in seconds. Defaults to 10.
        verify (bool, optional): Whether to verify SSL certificate. Defaults to True.
        enable_cache (bool, optional): Whether to use cache or not. Defaults to True.
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

    raise exceptions.RequestException(f"Maximum number of attempts exceeded for {url}")
