import pytest
import json

# 1. Teste de Conversão Base64 - Parametrizado
@pytest.mark.parametrize("params, expected", [
    ('{"page": 1}', "eyJwYWdlIjogMX0="),
    ('{"index": "IBOV"}', "eyJpbmRleCI6ICJJQk9WIn0="),
])
def test_params_to_base64(params, expected):
    from src.brdata.b3 import params_to_base64
    assert params_to_base64(params) == expected

# 2. Teste de Sucesso - Download Simples
def test_download_index_sucess(mocker):
    # Mock do requests para retornar JSON da B3
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "10/01/2026"},
        "results": [{"cod": "PETR4", "part": "5.0"}],
        "page": {"totalPages": 1}
    }

    mocker.patch("src.brdata.b3.requests.get", return_value=mock_response)

    # Mocks de sistema de arquivos
    mocker.patch("src.brdata.b3.os.makedirs")
    mocker.patch("src.brdata.b3.os.path.exists", return_value=False)
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    from src.brdata.b3 import download_index
    filename = download_index("IBOV")
    
    assert filename == "IBOV_10-01-2026.json"
    mock_open.assert_called_once()

# 3. Teste de Paginação - Mesclagem de resultados
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

    # Simula duas chamadas sequenciais para o requests.get
    mock_get = mocker.patch("src.brdata.b3.requests.get", side_effect=[resp_pg1, resp_pg2])
    mocker.patch("src.brdata.b3.os.makedirs")
    mocker.patch("src.brdata.b3.os.path.exists", return_value=False)
    mocker.patch("src.brdata.b3.time.sleep") # Remove espera real para o teste ser rápido
    
    mock_json_dump = mocker.patch("src.brdata.b3.json.dump")
    mocker.patch("builtins.open", mocker.mock_open())

    from src.brdata.b3 import download_index
    download_index("IBOV")

    assert mock_get.call_count == 2
    dados_finais = mock_json_dump.call_args[0][0]
    assert len(dados_finais) == 2
    assert dados_finais[1]["cod"] == "VALE3"

# 4. Teste de Validação - Pular índices inválidos
def test_download_indexes_skips_invalid(mocker):
    mock_singular = mocker.patch("src.brdata.b3.download_index")
    # Mock do tqdm como MagicMock para suportar tqdm.write()
    mock_tqdm = mocker.patch("src.brdata.b3.tqdm")
    mock_tqdm.side_effect = lambda x, **kwargs: x
    
    from src.brdata.b3 import download_indexes
    
    lista_teste = ["IBOV", "MOEDA_FAKE"]
    download_indexes(lista_teste)
    
    # Deve baixar apenas o IBOV
    assert mock_singular.call_count == 1
    mock_tqdm.write.assert_called_once_with("Index MOEDA_FAKE Not Found")

# 5. Teste de Erro - Resultados vazios
def test_download_index_raises_exception_on_empty_results(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "header": {"date": "15/04/2026"},
        "results": [], 
        "page": {"totalPages": 0}
    }
    mocker.patch("src.brdata.b3.requests.get", return_value=mock_response)
    mocker.patch("src.brdata.b3.os.makedirs")

    from src.brdata.b3 import download_index
    
    with pytest.raises(Exception, match="Data Not Found for IBOV"):
        download_index("IBOV")

# 6. Teste de Inteligência - Respeitar Overwrite
def test_download_index_respects_overwrite(mocker):
    mocker.patch("src.brdata.b3.os.path.exists", return_value=True)
    mocker.patch("src.brdata.b3.os.makedirs")
    
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"header": {"date": "15/04/2026"}}
    mocker.patch("src.brdata.b3.requests.get", return_value=mock_response)

    from src.brdata.b3 import download_index
    
    result = download_index("IBOV", overwrite=False)
    
    assert result == "IBOV_15-04-2026.json"