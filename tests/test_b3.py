import pandas as pd
import pytest

from brdata import b3


def test_b3_indices_dict():
    result = b3.indices()

    assert isinstance(result, dict)
    assert len(result) == len(b3.INDICES)
    assert len(result) > 1
    assert result == b3.INDICES


def test_b3_indices_list():
    result = b3.indices(False)

    assert isinstance(result, list)
    assert len(result) == len(b3.INDICES)
    assert len(result) > 1
    assert result == list(b3.INDICES.keys())


@pytest.mark.parametrize("index", b3.INDICES.keys())
def test_b3_portfolio(index: str):
    b3.portfolio.clear_cache()
    result = b3.portfolio(index)

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) > 0
    assert len(result) > 0


def test_b3_portfolio_invalid_index():
    with pytest.raises(ValueError):
        b3.portfolio("INVALID")


def test_b3_cias():
    b3.cias.clear_cache()
    result = b3.cias()

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) > 0
    assert len(result) > 0


def test_b3_bdrs():
    b3.bdrs.clear_cache()
    result = b3.bdrs()

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) > 0
    assert len(result) > 0


def test_b3_company_detail():
    b3.company_detail.clear_cache()
    result = b3.company_detail("25135")

    assert isinstance(result, pd.Series)
    assert len(result) > 0
