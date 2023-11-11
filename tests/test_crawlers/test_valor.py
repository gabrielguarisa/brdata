import brdata
import pandas as pd
import pytest


@pytest.mark.offline
def test_create_valor_crawler():
    crawler = brdata.ValorEconomicoCrawler()
    assert (
        crawler.url == "https://infograficos.valor.globo.com/carteira-valor/historico"
    )
    assert isinstance(crawler, brdata.ValorEconomicoCrawler)


@pytest.mark.offline
def test_valor_format_dataframe():
    data = [
        {
            "Nome  Nome/Código": "VALE ON  VALE3",
            "Código": "VALE3",
            "Indicações": 7,
            "Variação no mês  Var. Mês": "+6,33%",
        },
        {
            "Nome  Nome/Código": "PETRO RIO ON  PRIO3",
            "Código": "PRIO3",
            "Indicações": 7,
            "Variação no mês  Var. Mês": "+13,14%",
        },
        {
            "Nome  Nome/Código": "MULTIPLAN ON  MULT3",
            "Código": "MULT3",
            "Indicações": 6,
            "Variação no mês  Var. Mês": "+8,63%",
        },
    ]
    df = pd.DataFrame(data)
    result = brdata.ValorEconomicoCrawler._format_dataframe(df)

    assert isinstance(result, pd.DataFrame)
    assert "name" in result.columns
    assert "code" in result.columns
    assert "recommendations" in result.columns
    assert "month_variation" in result.columns
    assert "Nome  Nome/Código" not in result.columns
    assert "Código" not in result.columns
    assert "Indicações" not in result.columns
    assert "Variação no mês  Var. Mês" not in result.columns


@pytest.mark.online
def test_valor_get_recommended_wallet_by_month():
    crawler = brdata.ValorEconomicoCrawler()
    result = crawler.get_recommended_wallet_by_month(1, 2022, enable_cache=False)
    assert isinstance(result, pd.DataFrame)
    assert "name" in result.columns
    assert "code" in result.columns
    assert "recommendations" in result.columns
    assert "month_variation" in result.columns

    assert len(result) > 0


@pytest.mark.online
def test_valor_get_wallets_from_institutions_by_month():
    crawler = brdata.ValorEconomicoCrawler()
    result = crawler.get_wallets_from_institutions_by_month(1, 2022, enable_cache=False)
    assert isinstance(result, pd.DataFrame)
    assert "name" in result.columns
    assert "code" in result.columns
    assert "month_variation" in result.columns
    assert "institution" in result.columns

    assert len(result) > 0


@pytest.mark.online
def test_valor_get_recommended_wallet_by_month_with_invalid_year():
    crawler = brdata.ValorEconomicoCrawler()
    with pytest.raises(Exception):
        crawler.get_recommended_wallet_by_month(1, 1999, enable_cache=False)