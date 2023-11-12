class BaseException(Exception):
    """Base exception for all brdata exceptions."""

    pass


class RequestException(BaseException):
    """Exception raised when the maximum number of retries is reached."""

    def __init__(
        self, message: str = "Maximum number of retries reached.", *args, **kwargs
    ):
        super().__init__(message, *args, **kwargs)


class NotFoundException(BaseException):
    """Exception raised when some resource is not founds."""

    pass
