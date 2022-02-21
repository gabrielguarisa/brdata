"""brdata"""
import sys

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata  # pragma: no cover

from . import cvm, fundamentus, xpi


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


__version__: str = get_version()
__all__: list = ["__version__", "xpi", "fundamentus", "cvm"]
