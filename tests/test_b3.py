import pytest
import json

@pytest.mark.parametrize("params, expected", [
    ('{"page": 1}', "eyJwYWdlIjogMX0="),
    ('{"index": "IBOV"}', "eyJpbmRleCI6ICJJQk9WIn0="),
])
def test_params_to_base64(params, expected):
    from src.b3 import params_to_base64
    assert params_to_base64(params) == expected

def test_download_index_sucess(mocker):
    # requests mock to return b3 json
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "10/01/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1}
    }

    mocker.patch("src.b3.requests.get", return_value=mock_response)

    # os mock
    mocker.patch("src.b3.os.makedirs")
    mocker.patch("src.b3.os.path.exists", return_value=False)
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    from src.b3 import download_index
    filename = download_index("IBOV")
    assert filename == "IBOV_10-01-2026.json"
    mock_open.assert_called_once()

def test_download_index_pagination_merging(mocker):
    resp_pg1 = mocker.Mock()
    resp_pg1.status_code = 200
    resp_pg1.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 2}  
    }
    
    resp_pg2 = mocker.Mock()
    resp_pg2.status_code = 200
    resp_pg2.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [{"cod": "VALE3", "part": "7.0"}],
        "page": {"totalPages": 2} 
    }

    mock_get = mocker.patch("src.b3.requests.get", side_effect=[resp_pg1, resp_pg2])
    mocker.patch("src.b3.os.makedirs")
    mocker.patch("src.b3.os.path.exists", return_value=False)
    mocker.patch("src.b3.time.sleep") 
    
    mock_json_dump = mocker.patch("src.b3.json.dump")
    mocker.patch("builtins.open", mocker.mock_open())

    from src.b3 import download_index
    download_index("IBOV")

    assert mock_get.call_count == 2
    dados_finais = mock_json_dump.call_args[0][0]
    assert len(dados_finais) == 2
    assert dados_finais[1]["cod"] == "VALE3"

def test_download_indexes_skips_invalid(mocker):
    mock_singular = mocker.patch("src.b3.download_index")
    mock_tqdm = mocker.patch("src.b3.tqdm")
    mock_tqdm.side_effect = lambda x, **kwargs: x
    
    from src.b3 import download_indexes
    
    lista_teste = ["IBOV", "MOEDA_FAKE"]
    download_indexes(lista_teste)
    assert mock_singular.call_count == 1
    mock_tqdm.write.assert_called_once_with("Index MOEDA_FAKE Not Found")

def test_download_index_raises_exception_on_empty_results(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [], 
        "page": {"totalPages": 0}
    }
    mocker.patch("src.b3.requests.get", return_value=mock_response)
    mocker.patch("src.b3.os.makedirs")

    from src.b3 import download_index
    
    with pytest.raises(Exception, match="Data Not Found for IBOV"):
        download_index("IBOV")

def test_download_index_respects_overwrite(mocker):
    mocker.patch("src.b3.os.path.exists", return_value=True)
    mocker.patch("src.b3.os.makedirs")
    
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"header": {"date": "15/04/2026"}}
    mocker.patch("src.b3.requests.get", return_value=mock_response)

    from src.b3 import download_index
    
    result = download_index("IBOV", overwrite=False)
    
    assert result == "IBOV_15-04-2026.json"