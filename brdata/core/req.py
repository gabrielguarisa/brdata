import requests
from random_user_agent.user_agent import UserAgent

user_agent_rotator = UserAgent()


def new_user_agent() -> str:
    """Retorna um novo User-Agent."""
    return user_agent_rotator.get_random_user_agent()


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
