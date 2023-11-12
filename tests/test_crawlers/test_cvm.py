import brdata
import pandas as pd
import pytest


@pytest.mark.online
def test_cvm_crawler():
    crawler = brdata.CVMCrawler()

    # Test get_documents_by_year
    dfp_2018 = crawler.get_documents_by_year("DFP", 2018, enable_cache=False)
    assert isinstance(dfp_2018, dict)
    for df in dfp_2018.values():
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
