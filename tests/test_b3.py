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


def test_download_index_raises_on_invalid_index():
    with pytest.raises(ValueError, match="Index MOEDA_FAKE Not Found"):
        b3.download_index("MOEDA_FAKE")


# 2. Teste de Sucesso - Download Simples
def test_download_index_sucess(mocker):
    # Mock do requests para retornar JSON da B3
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "10/01/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }

    mocker.patch("brdata.b3.requests.get", return_value=mock_response)

    # Mocks de sistema de arquivos
    mock_makedirs = mocker.patch("brdata.b3.os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    data = b3.download_index(b3.B3Index.IBOV)

    assert data == {
        "header": {"date": "10/01/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
    }
    mock_makedirs.assert_not_called()
    mock_open.assert_not_called()


# 3. Teste de Paginação - Mesclagem de resultados
def test_download_index_pagination_merging(mocker):
    resp_pg1 = mocker.Mock()
    resp_pg1.status_code = 200
    resp_pg1.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 2},
    }

    resp_pg2 = mocker.Mock()
    resp_pg2.status_code = 200
    resp_pg2.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [{"cod": "VALE3", "part": "7.0"}],
        "page": {"totalPages": 2},
    }

    # Simula duas chamadas sequenciais para o requests.get
    mock_get = mocker.patch("brdata.b3.requests.get", side_effect=[resp_pg1, resp_pg2])
    mocker.patch("brdata.b3.os.makedirs")
    mocker.patch("brdata.b3.os.path.exists", return_value=False)
    mocker.patch("brdata.b3.time.sleep")  # Remove espera real para o teste ser rápido

    mock_json_dump = mocker.patch("brdata.b3.json.dump")
    mocker.patch("builtins.open", mocker.mock_open())

    b3.download_index("IBOV", path="data/landing/b3")

    assert mock_get.call_count == 2
    dados_finais = mock_json_dump.call_args[0][0]
    assert len(dados_finais["results"]) == 2
    assert dados_finais["results"][1]["cod"] == "VALE3"


# 4. Teste de Validação - Pular índices inválidos
def test_download_indexes_skips_invalid(mocker):
    index_data = {"header": {"date": "10/01/2026"}, "results": []}
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
        "header": {"date": "15/04/2026"},
        "results": [],
        "page": {"totalPages": 0},
    }
    mocker.patch("brdata.b3.requests.get", return_value=mock_response)
    mocker.patch("brdata.b3.os.makedirs")

    with pytest.raises(Exception, match="Data Not Found for IBOV"):
        b3.download_index("IBOV")


# 6. Teste de Inteligência - Respeitar Overwrite
def test_download_index_respects_overwrite(mocker):
    mocker.patch("brdata.b3.os.path.exists", return_value=True)
    mocker.patch("brdata.b3.os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open(read_data='{"cached": true}'))

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"header": {"date": "15/04/2026"}}
    mocker.patch("brdata.b3.requests.get", return_value=mock_response)

    result = b3.download_index("IBOV", path="data/landing/b3", overwrite=False)

    assert result == {"cached": True}
