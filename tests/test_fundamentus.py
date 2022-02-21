import pandas as pd

from brdata import fundamentus


def test_fundamentus_resultados():
    result = fundamentus.resultados()

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 1
    assert len(result.columns) > 1


def test_fundamentus_balanco_historico():
    balanco, demonstrativo = fundamentus.balanco_historico("mglu3")

    assert isinstance(balanco, pd.DataFrame)
    assert isinstance(demonstrativo, pd.DataFrame)

    assert len(balanco) > 1
    assert len(demonstrativo) > 1

    assert len(balanco.columns) > 1
    assert len(demonstrativo.columns) > 1
