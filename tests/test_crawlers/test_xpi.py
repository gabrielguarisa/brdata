import brdata
import pytest
import pandas as pd


@pytest.mark.online
def test_xpi_crawler():
    crawler = brdata.XPICrawler()
    analysis = crawler.get_analysis("petr3", enable_cache=False)
    assert analysis is not None
    assert isinstance(analysis, pd.Series)


@pytest.mark.online
def test_xpi_crawler_with_invalid_code():
    crawler = brdata.XPICrawler()
    with pytest.raises(brdata.exceptions.NotFoundException):
        _ = crawler.get_analysis("INVALID_CODE")
