import pytest

def test_crawler_finds_correct_link(mocker):
    html_content = '<html><a href="fca_2024.zip">Relatório 2024</a></html>'

    # Mock requests.get
    mock_get = mocker.patch("src.cvm.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html_content

    from src.cvm import crawler
    result = crawler("http://link-falso.com", "2024")

    assert result == "fca_2024.zip"
    mock_get.assert_called_once()

def test_dataset_raises_exception_when_not_found(mocker):
    mocker.patch("src.cvm.crawler", return_value=None)

    from src.cvm import dataset

    with pytest.raises(Exception, match="Download Failure"):
        dataset(2025, "ITR")

def tests_datasets_in_range_calls_dataset_multiple_times(mocker):
    mock_dataset = mocker.patch("src.cvm.dataset")
    mocker.patch("src.cvm.tqdm", lambda x, **kwargs: x)

    from src.cvm import datasets_in_range

    datasets_in_range("ITR", start_year=2021, last_year=2023)
    assert mock_dataset.call_count == 3

def test_crawler_no_link_found(mocker):
    html = '<html><a href="manual.pdf">Manual 2023</a><a href="dados_2022.zip">2022</a></html>'
    mock_get = mocker.patch("src.cvm.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html

    from src.cvm import crawler
    assert crawler("http://url.com", "2023") is None

def test_crawler_connection_error(mocker):
    import requests
    mocker.patch("src.cvm.requests.get", side_effect=requests.exceptions.ConnectionError)

    from src.cvm import crawler
    assert crawler("http://url.com", "2024") is None

def test_datasets_in_range_uses_default_rules(mocker):
    mock_dataset = mocker.patch("src.cvm.dataset")
    mocker.patch("src.cvm.tqdm", lambda x, **kwargs: x)

    from src.cvm import datasets_in_range
    datasets_in_range("ITR")
    
    assert mock_dataset.call_count == 15
    assert mock_dataset.call_args_list[0].kwargs['year'] == "2011"

def test_datasets_in_range_stop_on_exception(mocker):
    mocker.patch("src.cvm.dataset", side_effect=Exception("Fatal Error"))
    mocker.patch("src.cvm.tqdm", lambda x, **kwargs: x)

    from src.cvm import datasets_in_range
    with pytest.raises(Exception, match="Fatal Error"):
        datasets_in_range("DFP", start_year=2020, last_year=2022, skip_exceptions=False)
    
def test_dataset_overwrite_behavior(mocker):
    mocker.patch("src.cvm.os.path.isfile", return_value=True)
    mocker.patch("src.cvm.os.makedirs")
    mocker.patch("src.cvm.crawler", return_value="arquivo.zip")

    mock_get = mocker.patch("src.cvm.requests.get")

    from src.cvm import dataset
    dataset(2023, "FCA", overwrite=False)
    mock_get.assert_not_called()

    mock_get.return_value.status_code = 200
    mock_get.return_value.iter_content = lambda chunk_size: [b"dados"]
    mocker.patch("builtins.open", mocker.mock_open())

    dataset(2023, "FCA", overwrite=True)
    assert mock_get.call_count == 1