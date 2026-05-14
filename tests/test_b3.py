import base64
import json
from enum import StrEnum

import pytest
from brdata import b3


# 1. Teste de Conversão Base64 - Parametrizado
@pytest.mark.parametrize(
    "params, expected",
    [
        ('{"page": 1}', "eyJwYWdlIjogMX0="),
        ('{"index": "IBOV"}', "eyJpbmRleCI6ICJJQk9WIn0="),
    ],
)
def test_params_to_base64(params, expected):
    assert b3.params_to_base64(params) == expected


def test_b3_index_is_str_enum():
    assert issubclass(b3.B3Index, StrEnum)
    assert b3.B3Index.IBOV.value == "IBOV"
    assert b3.B3Index.IBOV == "IBOV"


def test_list_indexes_returns_available_indexes():
    indexes = b3.list_indexes()

    assert indexes[0] == "IBOV"
    assert "IFIX" in indexes
    assert indexes == [index.value for index in b3.B3Index]


def test_format_date_to_iso_raises_on_invalid_date():
    with pytest.raises(ValueError, match="Invalid B3 date format: 2026-05-14"):
        b3._format_date_to_iso("2026-05-14")


def test_download_index_raises_on_invalid_index():
    with pytest.raises(ValueError, match="Index MOEDA_FAKE Not Found"):
        b3.download_index("MOEDA_FAKE")


# 2. Teste de Sucesso - Download Simples
def test_download_index_sucess(mocker):
    # Mock do requests para retornar JSON da B3
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }

    mock_get = mocker.patch("brdata.b3.requests.get", return_value=mock_response)

    # Mocks de sistema de arquivos
    mock_makedirs = mocker.patch("brdata.b3.os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    data = b3.download_index("ibov")

    assert data == {
        "results": [{"cod": "PETR4", "part": "5.0"}],
    }
    encoded_params = mock_get.call_args.args[0].rsplit("/", 1)[1]
    params = json.loads(base64.b64decode(encoded_params).decode("utf-8"))
    assert params["language"] == "en-us"
    assert params["index"] == "IBOV"
    assert "segment" not in params
    mock_makedirs.assert_not_called()
    mock_open.assert_not_called()


def test_download_index_day_portfolio_includes_date_and_segment(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "05/14/26"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }
    mock_get = mocker.patch("brdata.b3.requests.get", return_value=mock_response)

    data = b3.download_index("ibov", theoretical=False)

    assert data == {
        "date": "2026-05-14",
        "results": [{"cod": "PETR4", "part": "5.0"}],
    }
    assert "GetPortfolioDay" in mock_get.call_args.args[0]
    encoded_params = mock_get.call_args.args[0].rsplit("/", 1)[1]
    params = json.loads(base64.b64decode(encoded_params).decode("utf-8"))
    assert params["segment"] == "1"


def test_download_index_day_portfolio_raises_when_date_missing(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }
    mocker.patch("brdata.b3.requests.get", return_value=mock_response)

    with pytest.raises(Exception, match="Date Not Found for IBOV"):
        b3.download_index("IBOV", theoretical=False)


# 3. Teste de Paginação - Mesclagem de resultados
def test_download_index_pagination_merging(mocker):
    resp_pg1 = mocker.Mock()
    resp_pg1.status_code = 200
    resp_pg1.json.return_value = {
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 2},
    }

    resp_pg2 = mocker.Mock()
    resp_pg2.status_code = 200
    resp_pg2.json.return_value = {
        "results": [{"cod": "VALE3", "part": "7.0"}],
        "page": {"totalPages": 2},
    }

    # Simula duas chamadas sequenciais para o requests.get
    mock_get = mocker.patch("brdata.b3.requests.get", side_effect=[resp_pg1, resp_pg2])
    mocker.patch("brdata.b3.os.makedirs")
    mocker.patch("brdata.b3.os.path.exists", return_value=False)
    mocker.patch("brdata.b3.time.sleep")  # Remove espera real para o teste ser rápido

    mock_json_dump = mocker.patch("brdata.b3.json.dump")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    b3.download_index("IBOV", path="data/landing/b3")

    assert mock_get.call_count == 2
    dados_finais = mock_json_dump.call_args[0][0]
    assert len(dados_finais["results"]) == 2
    assert dados_finais["results"][1]["cod"] == "VALE3"
    mock_open.assert_called_once_with(
        "data/landing/b3/IBOV.json", "w", encoding="utf-8"
    )


def test_download_index_day_portfolio_uses_separate_file(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "05/14/26"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }
    mocker.patch("brdata.b3.requests.get", return_value=mock_response)
    mocker.patch("brdata.b3.os.makedirs")
    mocker.patch("brdata.b3.os.path.exists", return_value=False)
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    b3.download_index("IBOV", path="data/landing/b3", theoretical=False)

    mock_open.assert_called_once_with(
        "data/landing/b3/IBOV_day.json", "w", encoding="utf-8"
    )


# 4. Teste de Validação - Pular índices inválidos
def test_download_indexes_skips_invalid(mocker):
    index_data = {"results": []}
    mock_singular = mocker.patch(
        "brdata.b3.download_index",
        side_effect=[index_data, ValueError("Index MOEDA_FAKE Not Found")],
    )
    # Mock do tqdm como MagicMock para suportar tqdm.write()
    mock_tqdm = mocker.patch("brdata.b3.tqdm")
    mock_tqdm.side_effect = lambda x, **kwargs: x

    lista_teste = ["IBOV", "MOEDA_FAKE"]
    result = b3.download_indexes(lista_teste)

    # Deve baixar apenas o IBOV
    assert result == {"IBOV": index_data}
    assert mock_singular.call_count == 2
    mock_tqdm.write.assert_called_once_with("Index MOEDA_FAKE Not Found")


# 5. Teste de Erro - Resultados vazios
def test_download_index_raises_exception_on_empty_results(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [],
        "page": {"totalPages": 0},
    }
    mocker.patch("brdata.b3.requests.get", return_value=mock_response)
    mocker.patch("brdata.b3.os.makedirs")

    with pytest.raises(Exception, match="Data Not Found for IBOV"):
        b3.download_index("IBOV")


def test_download_index_raises_index_error_on_request_failure(mocker):
    mocker.patch("brdata.b3.requests.get", side_effect=Exception("Network Error"))

    with pytest.raises(Exception, match="Index Error IBOV: Network Error"):
        b3.download_index("IBOV")


# 6. Teste de Inteligência - Respeitar Overwrite
def test_download_index_respects_overwrite(mocker):
    mocker.patch("brdata.b3.os.path.exists", return_value=True)
    mocker.patch("brdata.b3.os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open(read_data='{"cached": true}'))

    result = b3.download_index("IBOV", path="data/landing/b3", overwrite=False)

    assert result == {"cached": True}
