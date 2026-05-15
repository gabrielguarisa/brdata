import base64
import json
from enum import StrEnum

import pytest
from brdata.b3 import indexes


@pytest.mark.parametrize(
    "params, expected",
    [
        ('{"page": 1}', "eyJwYWdlIjogMX0="),
        ('{"index": "IBOV"}', "eyJpbmRleCI6ICJJQk9WIn0="),
    ],
)
def test_params_to_base64(params, expected):
    assert indexes.params_to_base64(params) == expected


def test_b3_index_is_str_enum():
    assert issubclass(indexes.B3Index, StrEnum)
    assert indexes.B3Index.IBOV.value == "IBOV"
    assert indexes.B3Index.IBOV == "IBOV"


def test_list_indexes_returns_available_indexes():
    available_indexes = indexes.list_indexes()

    assert available_indexes[0] == "IBOV"
    assert "IFIX" in available_indexes
    assert available_indexes == [index.value for index in indexes.B3Index]


def test_format_date_to_iso_raises_on_invalid_date():
    with pytest.raises(ValueError, match="Invalid B3 date format: 2026-05-14"):
        indexes._format_date_to_iso("2026-05-14")


def test_download_index_raises_on_invalid_index():
    with pytest.raises(ValueError, match="Index MOEDA_FAKE Not Found"):
        indexes.download_index("MOEDA_FAKE")


def test_download_index_sucess(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1},
    }

    mock_get = mocker.patch("brdata.b3.indexes.requests.get", return_value=mock_response)
    mock_makedirs = mocker.patch("brdata.b3.indexes.os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    data = indexes.download_index("ibov")

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
    mock_get = mocker.patch("brdata.b3.indexes.requests.get", return_value=mock_response)

    data = indexes.download_index("ibov", theoretical=False)

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
    mocker.patch("brdata.b3.indexes.requests.get", return_value=mock_response)

    with pytest.raises(Exception, match="Date Not Found for IBOV"):
        indexes.download_index("IBOV", theoretical=False)


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

    mock_get = mocker.patch(
        "brdata.b3.indexes.requests.get", side_effect=[resp_pg1, resp_pg2]
    )
    mocker.patch("brdata.b3.indexes.os.makedirs")
    mocker.patch("brdata.b3.indexes.os.path.exists", return_value=False)
    mocker.patch("brdata.b3.indexes.time.sleep")

    mock_json_dump = mocker.patch("brdata.b3.indexes.json.dump")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    indexes.download_index("IBOV", path="data/landing/b3")

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
    mocker.patch("brdata.b3.indexes.requests.get", return_value=mock_response)
    mocker.patch("brdata.b3.indexes.os.makedirs")
    mocker.patch("brdata.b3.indexes.os.path.exists", return_value=False)
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    indexes.download_index("IBOV", path="data/landing/b3", theoretical=False)

    mock_open.assert_called_once_with(
        "data/landing/b3/IBOV_day.json", "w", encoding="utf-8"
    )


def test_download_indexes_skips_invalid(mocker):
    index_data = {"results": []}
    mock_singular = mocker.patch(
        "brdata.b3.indexes.download_index",
        side_effect=[index_data, ValueError("Index MOEDA_FAKE Not Found")],
    )
    mock_tqdm = mocker.patch("brdata.b3.indexes.tqdm")
    mock_tqdm.side_effect = lambda x, **kwargs: x

    lista_teste = ["IBOV", "MOEDA_FAKE"]
    result = indexes.download_indexes(lista_teste)

    assert result == {"IBOV": index_data}
    assert mock_singular.call_count == 2
    mock_tqdm.write.assert_called_once_with("Index MOEDA_FAKE Not Found")


def test_download_index_raises_exception_on_empty_results(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [],
        "page": {"totalPages": 0},
    }
    mocker.patch("brdata.b3.indexes.requests.get", return_value=mock_response)
    mocker.patch("brdata.b3.indexes.os.makedirs")

    with pytest.raises(Exception, match="Data Not Found for IBOV"):
        indexes.download_index("IBOV")


def test_download_index_raises_index_error_on_request_failure(mocker):
    mocker.patch("brdata.b3.indexes.requests.get", side_effect=Exception("Network Error"))

    with pytest.raises(Exception, match="Index Error IBOV: Network Error"):
        indexes.download_index("IBOV")


def test_download_index_respects_overwrite(mocker):
    mocker.patch("brdata.b3.indexes.os.path.exists", return_value=True)
    mocker.patch("brdata.b3.indexes.os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open(read_data='{"cached": true}'))

    result = indexes.download_index("IBOV", path="data/landing/b3", overwrite=False)

    assert result == {"cached": True}
