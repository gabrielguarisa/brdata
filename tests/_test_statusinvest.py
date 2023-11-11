import pandas as pd

from brdata import statusinvest


def test_proventos():
    data = statusinvest.proventos("CYRE3", True)
    assert isinstance(data, pd.DataFrame)
