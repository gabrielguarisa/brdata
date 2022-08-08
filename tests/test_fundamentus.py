import pandas as pd

from brdata import fundamentus


def test_fundamentus_resultados():
    fundamentus.resultados.clear_cache()
    result = fundamentus.resultados()

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 1
    assert len(result.columns) > 1


def test_fundamentus_balanco_historico():
    fundamentus.balanco_historico.clear_cache()
    balanco, demonstrativo = fundamentus.balanco_historico("mglu3")

    assert isinstance(balanco, pd.DataFrame)
    assert isinstance(demonstrativo, pd.DataFrame)

    assert len(balanco) > 1
    assert len(demonstrativo) > 1

    assert len(balanco.columns) > 1
    assert len(demonstrativo.columns) > 1


def test_fundamentus_detalhes():
    fundamentus.detalhes.clear_cache()
    detalhes = fundamentus.detalhes("bbas3", ravel=False)

    assert isinstance(detalhes, dict)
    assert len(detalhes) > 1

    for col in [
        "Metadata",
        "Oscilações",
        "Indicadores fundamentalistas",
        "Dados Balanço Patrimonial",
        "Dados demonstrativos de resultados",
    ]:
        assert col in detalhes


def test_fundamentus_detalhes_with_ravel():
    fundamentus.detalhes.clear_cache()
    detalhes = fundamentus.detalhes("bbas3")

    assert isinstance(detalhes, pd.Series)
    assert len(detalhes) > 1
