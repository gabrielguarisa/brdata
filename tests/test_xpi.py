import pandas as pd

from brdata import xpi


def test_xpi_analise():
    xpi.analise.clear_cache()
    result = xpi.analise("cyre3")
    assert isinstance(result, pd.Series)
    assert len(result) > 1
