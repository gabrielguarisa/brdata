import pytest
import requests

# 1. Teste do Crawler - Sucesso
def test_crawler_finds_correct_link(mocker):
    html_content = '<html><a href="fca_2024.zip">Relatório 2024</a></html>'

    # Mockamos o requests dentro do novo caminho
    mock_get = mocker.patch("src.brdata.cvm.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html_content

    from src.brdata.cvm import crawler
    result = crawler("http://link-falso.com", "2024")

    assert result == "fca_2024.zip"
    mock_get.assert_called_once()

# 2. Teste de Dataset - Arquivo não encontrado
def test_dataset_raises_exception_when_not_found(mocker):
    # Mock do crawler interno
    mocker.patch("src.brdata.cvm.crawler", return_value=None)

    from src.brdata.cvm import dataset

    with pytest.raises(Exception, match="Download Failure"):
        dataset(2025, "ITR")

# 3. Teste de Range - Múltiplas chamadas
def tests_datasets_in_range_calls_dataset_multiple_times(mocker):
    # Corrigido para apontar para o local exato onde a função reside
    mock_dataset = mocker.patch("src.brdata.cvm.dataset")
    mocker.patch("src.brdata.cvm.tqdm", lambda x, **kwargs: x)

    from src.brdata.cvm import datasets_in_range

    datasets_in_range("ITR", start_year=2021, last_year=2023)
    
    # 2021, 2022, 2023 = 3 chamadas
    assert mock_dataset.call_count == 3

# 4. Teste do Crawler - Link não encontrado no HTML
def test_crawler_no_link_found(mocker):
    html = '<html><a href="manual.pdf">Manual 2023</a><a href="dados_2022.zip">2022</a></html>'
    mock_get = mocker.patch("src.brdata.cvm.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html

    from src.brdata.cvm import crawler
    assert crawler("http://url.com", "2023") is None

# 5. Teste do Crawler - Erro de Conexão
def test_crawler_connection_error(mocker):
    mocker.patch("src.brdata.cvm.requests.get", side_effect=requests.exceptions.ConnectionError)

    from src.brdata.cvm import crawler
    assert crawler("http://url.com", "2024") is None

# 6. Teste de Range - Regras Padrão (DEFAULT_RULES)
def test_datasets_in_range_uses_default_rules(mocker):
    mock_dataset = mocker.patch("src.brdata.cvm.dataset")
    mocker.patch("src.brdata.cvm.tqdm", lambda x, **kwargs: x)

    from src.brdata.cvm import datasets_in_range
    datasets_in_range("ITR")
    
    # ITR padrão é 2011 a 2025 = 15 anos
    assert mock_dataset.call_count == 15
    assert mock_dataset.call_args_list[0].kwargs['year'] == "2011"

# 7. Teste de Range - Parada em caso de Erro
def test_datasets_in_range_stop_on_exception(mocker):
    mocker.patch("src.brdata.cvm.dataset", side_effect=Exception("Fatal Error"))
    mocker.patch("src.brdata.cvm.tqdm", lambda x, **kwargs: x)

    from src.brdata.cvm import datasets_in_range
    with pytest.raises(Exception, match="Fatal Error"):
        datasets_in_range("DFP", start_year=2020, last_year=2022, skip_exceptions=False)
    
# 8. Teste de Dataset - Comportamento do Overwrite
def test_dataset_overwrite_behavior(mocker):
    mocker.patch("src.brdata.cvm.os.path.isfile", return_value=True)
    mocker.patch("src.brdata.cvm.os.makedirs")
    mocker.patch("src.brdata.cvm.crawler", return_value="arquivo.zip")

    mock_get = mocker.patch("src.brdata.cvm.requests.get")

    from src.brdata.cvm import dataset
    
    # Teste 1: Não deve baixar se já existe e overwrite é False
    dataset(2023, "FCA", overwrite=False)
    mock_get.assert_not_called()

    # Teste 2: Deve baixar se overwrite é True
    mock_get.return_value.status_code = 200
    mock_get.return_value.iter_content = lambda chunk_size: [b"dados"]
    mocker.patch("builtins.open", mocker.mock_open())

    dataset(2023, "FCA", overwrite=True)
    assert mock_get.call_count == 1