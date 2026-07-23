import pytest
from unittest.mock import patch, MagicMock
from urllib.parse import unquote
import requests

from src.brdata.bacen.boletim_focus import BoletimFocus

@pytest.fixture
def boletim():
    return BoletimFocus()

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {"value": [{"indicador": "IPCA", "Data": "2023-01-01"}]}
    mock.raise_for_status.return_value = None
    return mock

@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_get_chamada_basica_sem_filtros(mock_get, boletim, mock_response):
    mock_get.return_value = mock_response
    
    resultado = boletim._get(endpoint="ExpectativaMercadoMensais")
    
    mock_get.assert_called_once()
    
    url_chamada = unquote(mock_get.call_args[0][0])
    assert "ExpectativaMercadoMensais" in url_chamada
    assert "$top=100" in url_chamada
    assert "$format=json" in url_chamada
    
    assert resultado == [{"indicador": "IPCA", "Data": "2023-01-01"}]

@patch("src.brdata.bacen.boletim_focus.date_validator")
@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_get_chamada_com_filtros(mock_get, mock_date_val, boletim, mock_response):
    mock_get.return_value = mock_response
    mock_date_val.side_effect = lambda x: x 
    
    boletim._get(
        endpoint="TesteEndpoint",
        indicador="Selic",
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
    
    url_chamada = unquote(mock_get.call_args[0][0])
    
    assert "Indicador eq 'Selic'" in url_chamada
    assert "Data ge '2023-01-01'" in url_chamada
    assert "Data le '2023-12-31'" in url_chamada
    
    assert mock_date_val.call_count == 2

@patch("src.brdata.bacen.boletim_focus.write_to_disk")
@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_get_salvamento_em_disco(mock_get, mock_write, boletim, mock_response):
    mock_get.return_value = mock_response
    
    boletim._get("ExpectativaMercadoMensais", path="/meu/diretorio/")
    
    dados_esperados = [{"indicador": "IPCA", "Data": "2023-01-01"}]
    nome_arquivo = "ExpectativaMercadoMensais.json"
    
    mock_write.assert_called_once_with(dados_esperados, nome_arquivo, "/meu/diretorio/")

@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_get_erro_de_requisicao(mock_get, boletim):
    mock_erro = MagicMock()
    mock_erro.raise_for_status.side_effect = requests.exceptions.HTTPError("Erro 404")
    mock_get.return_value = mock_erro
    
    with pytest.raises(requests.exceptions.HTTPError):
        boletim._get("QualquerEndpoint")

@patch.object(BoletimFocus, '_get')
def test_endpoint_expectativas_mensais(mock_get, boletim):
    boletim.expectativas_mensais(
        indicador="IPCA", 
        start_date="2023-01-01", 
        top=50, 
        path="./dados"
    )
    
    mock_get.assert_called_once_with(
        "ExpectativaMercadoMensais", 
        "IPCA", 
        "2023-01-01", 
        None, 
        50, 
        "./dados"
    )

@patch.object(BoletimFocus, '_get')
def test_endpoint_top5_selic(mock_get, boletim):
    boletim.top5_selic()
    
    mock_get.assert_called_once_with(
        "ExpectativasMercadoTop5Selic", 
        None, None, None, 100, None
    )
