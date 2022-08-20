import pandas as pd

from brdata import valor


def test_valor_portfolios():
    valor.portfolios.clear_cache()
    result = valor.portfolios(2, 2020)

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) == 2
    assert result.columns.values.tolist() == ["Research", "Papel"]
    assert len(result) > 0


def test_valor_portfolios_without_melt():
    valor.portfolios.clear_cache()
    result = valor.portfolios(2, 2020, melt=False)

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) > 0
    assert len(result) > 0


def test_valor_carteira_valor():
    valor.carteira_valor.clear_cache()
    result = valor.carteira_valor(2, 2020)

    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) > 0
    assert len(result) > 0
