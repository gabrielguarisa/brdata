import pytest
from unittest.mock import patch, MagicMock
from datetime import date
import requests

from src.brdata.bacen.boletim_focus import FocusEndpoint, list_endpoints, fetch_boletim_focus

def test_list_endpoints():
    """Garante que list_endpoints retorna todos os valores corretos do Enum."""
    endpoints = list_endpoints()
    
    assert isinstance(endpoints, list)
    assert len(endpoints) == len(FocusEndpoint)
    assert "ExpectativaMercadoMensais" in endpoints
    assert "DatasReferencia" in endpoints

@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_fetch_boletim_focus_sucesso_padrao(mock_get):
    """Testa a chamada bem-sucedida com os parâmetros padrões (top=100, sem filtro)."""
    mock_response = MagicMock()
    dados_falsos = {"value": [{"Indicador": "IPCA", "Meta": 3.5}]}
    mock_response.json.return_value = dados_falsos
    mock_get.return_value = mock_response

    resultado = fetch_boletim_focus(FocusEndpoint.MERCADO_MENSAIS)

    assert resultado == dados_falsos
    
    mock_get.assert_called_once_with(
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativaMercadoMensais",
        {"$format": "json", "$top": 100}
    )


@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_fetch_boletim_focus_com_filtros_customizados(mock_get):
    """Testa se os parâmetros opcionais top e filter_expr são passados corretamente."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"value": []}
    mock_get.return_value = mock_response

    fetch_boletim_focus(
        endpoint=FocusEndpoint.MERCADO_SELIC,
        top=50,
        filter_expr="Indicador eq 'Selic' and Data eq '2026-05-20'"
    )

    mock_get.assert_called_once_with(
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoSelic", 
        {
            "$format": "json",
            "$top": 50,
            "$filter": "Indicador eq 'Selic' and Data eq '2026-05-20'"
        }
    )


@patch("src.brdata.bacen.boletim_focus.write_to_disk")
@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_fetch_boletim_focus_salvando_em_disco(mock_get, mock_write):
    """Testa a geração do nome do arquivo e escrita em disco quando path é fornecido."""
    mock_response = MagicMock()
    dados_falsos = {"value": ["dados"]}
    mock_response.json.return_value = dados_falsos
    mock_get.return_value = mock_response

    fetch_boletim_focus(FocusEndpoint.DATAS_REFERENCIA, path="/home/user/data")

    hoje = date.today()
    filename_esperado = f"boletim_focus_FocusEndpoint.DATAS_REFERENCIA_{hoje}.json"

    mock_write.assert_called_once_with(dados_falsos, filename_esperado, "/home/user/data")


@patch("src.brdata.bacen.boletim_focus.requests.get")
def test_fetch_boletim_focus_captura_e_repassa_erro(mock_get):
    """Garante que erros de requisição disparam a Exception personalizada com o nome do endpoint."""
    mock_get.side_effect = requests.exceptions.RequestException("Erro de conexão com o servidor do BACEN")

    with pytest.raises(Exception) as contexto_do_erro:
        fetch_boletim_focus(FocusEndpoint.INFLACAO_12M)

    assert "Failed to query the endpoint INFLACAO_12M" in str(contexto_do_erro.value)
    assert "Erro de conexão com o servidor do BACEN" in str(contexto_do_erro.value)