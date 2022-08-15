from brdata.cvm._utils import get_table_links


def test_get_table_links():
    url = "http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS"
    result = get_table_links(url)
    assert isinstance(result, dict)
