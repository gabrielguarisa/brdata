import json

import pandas as pd
import pytest

from brdata import valor


@pytest.fixture
def valor_response():
    with open("tests/resources/valor.json", "r") as f:
        response = json.load(f)
    return response


def test_valor():
    ve = valor.ValorEconomico(1, 2021)
    assert ve.year == "2021"
    assert ve.month == "01"
    assert ve.month_str == "jan"
    assert ve.year_2d == "21"
    assert (
        ve.url
        == "https://infovalorbucket.s3.amazonaws.com/arquivos/carteira-valor/historico/2021/01/jan21json.json"
    )


def test_valor_with_response(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    assert isinstance(ve.response, dict)
    assert ve.response == valor_response


def test_valor_carteira_valor(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    df = ve.carteira_valor()

    assert isinstance(df, pd.DataFrame)
    assert df.columns.to_list() == [
        "acao",
        "ticker",
        "variacao",
        "indicacoes",
        "qindicou",
        "path_360",
    ]
    assert df.shape == (10, 6)


def test_valor_carteira_valor_comportamento(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    df = ve.carteira_valor_comportamento()

    assert isinstance(df, pd.Series)
    assert df.shape == (4,)


def test_valor_carteira_valor_serie_historica(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    df = ve.carteira_valor_serie_historica()

    assert isinstance(df, pd.DataFrame)
    assert df.columns.to_list() == [
        "datas",
        "carteiravalor",
        "ibovespa",
    ]
    assert df.shape == (13, 3)


def test_valor_corretoras(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    df = ve.corretoras()

    assert isinstance(df, pd.DataFrame)
    assert df.columns.to_list() == ["acao", "ticker", "variacao", "path_360", "nome"]
    assert df.shape == (95, 5)


def test_valor_corretoras_serie_historica(valor_response):
    ve = valor.ValorEconomico(1, 2021, valor_response)
    df = ve.corretoras_serie_historica()

    assert isinstance(df, pd.DataFrame)
    assert df.columns.to_list() == [
        "datas",
        "Ágora Investimentos",
        "Ativa Investimentos",
        "BB Investimentos",
        "CM Capital Corretora",
        "Genial Investimentos",
        "Guide Investimentos",
        "Inter",
        "Mirae Corretora",
        "Modalmais",
        "MyCAP Investimentos",
        "Nova Futura Investimentos",
        "Órama",
        "Planner Corretora",
        "Safra Corretora",
        "Santander Corretora",
        "Terra Investimentos",
        "Toro Investimentos",
        "Warren",
        "XP Investimentos",
    ]
    assert df.shape == (13, 20)
