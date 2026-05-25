import pytest
import requests
from datetime import date
from unittest.mock import MagicMock

from src.brdata.bacen.currency import currency_price 

def test_currency_price_invalid_date_format():
    with pytest.raises(ValueError, match="The date is in an invalid format"):
        currency_price(currency="USD", price_date="2025-12-25")


def test_currency_price_invalid_end_date_format():
    with pytest.raises(ValueError, match="The date is in an invalid format"):
        currency_price(currency="USD", price_date="12-25-2025", end_price_date="25/12/2025")


def test_currency_price_single_day_success(mocker):
    mock_get = mocker.patch('requests.get')
  
    mock_res = mocker.Mock()
    mock_res.json.return_value = {"value": [{"cotacaoCompra": 5.20}]}
    mock_res.raise_for_status.return_value = None
    mock_get.return_value = mock_res

    result = currency_price(currency="USD", price_date="12-25-2025")
    
    assert result == {"value": [{"cotacaoCompra": 5.20}]}
    mock_get.assert_called_once_with(
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='USD'&@dataCotacao='12-25-2025'&$top=100&$format=json"
    )


def test_currency_price_period_success(mocker):
    mock_get = mocker.patch('requests.get')
    
    mock_res = mocker.Mock()
    mock_res.json.return_value = {"value": [{"cotacaoCompra": 5.50}]}
    mock_res.raise_for_status.return_value = None
    mock_get.return_value = mock_res

    result = currency_price(currency="EUR", price_date="12-20-2025", end_price_date="12-25-2025")
    
    assert result == {"value": [{"cotacaoCompra": 5.50}]}
    mock_get.assert_called_once_with(
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='EUR'&@dataInicial='12-20-2025'&@dataFinalCotacao='12-25-2025'&$top=100&$format=json"
    )


def test_currency_price_default_to_today(mocker):
    today_str = date.today().strftime('%m-%d-%Y')
    mock_get = mocker.patch('requests.get')
    
    mock_res = mocker.Mock()
    mock_res.json.return_value = {"data": "hoje"}
    mock_res.raise_for_status.return_value = None
    mock_get.return_value = mock_res

    result = currency_price(currency="USD")
    
    assert result == {"data": "hoje"}
    assert today_str in mock_get.call_args[0][0]


def test_currency_price_saves_to_path(mocker):
    mock_get = mocker.patch('requests.get')
    mock_write = mocker.patch('src.brdata.bacen.currency.write_to_disk') 
    
    mock_res = mocker.Mock()
    mock_res.json.return_value = {"moeda": "USD"}
    mock_res.raise_for_status.return_value = None
    mock_get.return_value = mock_res

    result = currency_price(currency="USD", price_date="12-25-2025", path="/path/to/save")

    assert result is None
    mock_write.assert_called_once_with({"moeda": "USD"}, "USD_12-25-2025.json", "/path/to/save")


def test_currency_price_http_error(mocker, capsys):
    mock_get = mocker.patch('requests.get')
    
    mock_res = mocker.Mock()
    mock_res.raise_for_status.side_effect = requests.exceptions.HTTPError("Erro interno simulado")
    mock_get.return_value = mock_res

    currency_price(currency="USD", price_date="12-25-2025")
    
    captured = capsys.readouterr()
    assert "Error:" in captured.out