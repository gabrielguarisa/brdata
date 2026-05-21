import pytest
from unittest.mock import patch, MagicMock
from datetime import date
import requests

from src.brdata.bacen.selic import fetch_selic

@patch("src.brdata.bacen.selic.requests.get")
def test_fetch_selic_meta_sucesso(mock_get):
    """testa a busca de selic meta com sucesso, sem salvar em arquivo"""
    mock_response = MagicMock()
    dados_falsos = [{"data": "20/05/2026", "valor": "10.50"}]
    mock_response.json.return_value = dados_falsos
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    resultado = fetch_selic(category="meta", start_date="01/05/2026")

    assert resultado == dados_falsos
    mock_get.assert_called_once_with(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados",
        params={"formato": "json", "dataInicial": "01/05/2026"}
    )

@patch("src.brdata.bacen.selic.requests.get")
def test_fetch_selic_diaria_com_data_final(mock_get):
    """Testa a busca de Selic Diária incluindo o parâmetro end_date."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    fetch_selic(
        category="diaria", start_date="01/01/2026", end_date="31/01/2026"
    )

    mock_get.assert_called_once_with(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados",
        params={
            "formato": "json",
            "dataInicial": "01/01/2026",
            "dataFinal": "31/01/2026",
        },
    )


@patch("src.brdata.bacen.selic.write_to_disk")
@patch("src.brdata.bacen.selic.requests.get")
def test_fetch_selic_salvando_no_disco(mock_get, mock_write):
    """Testa se a função chama corretamente o write_to_disk quando passamos um path."""
    mock_response = MagicMock()
    dados_falsos = [{"data": "20/05/2026", "valor": "10.50"}]
    mock_response.json.return_value = dados_falsos
    mock_get.return_value = mock_response

    resultado = fetch_selic(
        category="meta", start_date="20/05/2026", path="/downloads"
    )

    assert resultado is None

    mock_write.assert_called_once_with(
        dados_falsos, "selic_meta_20-05-2026.json", "/downloads"
    )


@patch("src.brdata.bacen.selic.requests.get")
def test_fetch_selic_erro_na_requisicao(mock_get, capsys):
    """Testa o comportamento da função quando a API falha."""
    mock_get.side_effect = requests.exceptions.RequestException(
        "Erro de Conexão"
    )

    resultado = fetch_selic(category="meta", start_date="01/05/2026")

    assert resultado is None

    captured = capsys.readouterr()
    assert "Error: Erro de Conexão" in captured.out