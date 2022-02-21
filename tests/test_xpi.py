import pandas as pd

from brdata import xpi


def test_xpi_analise():
    result = xpi.analise("cyre3")
    assert isinstance(result, pd.Series)
    assert len(result) > 1
