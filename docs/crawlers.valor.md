<!-- markdownlint-disable -->

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `crawlers.valor`






---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ValorEconomicoCrawler`
Crawler for Valor Economico. 



**Examples:**
 

```python
import brdata
crawler = brdata.ValorEconomicoCrawler()
crawler.get_recommended_wallet_by_month(1, 2022)
``` 

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```








---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_page_soup`

```python
get_page_soup(
    month: int,
    year: int,
    enable_cache: bool = True,
    **kwargs
) → BeautifulSoup
```





---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_recommended_wallet`

```python
get_recommended_wallet(
    start_date: str,
    end_date: str,
    to_pandas: bool = True,
    enable_cache: bool = True
)
```

Get recommended wallet. 



**Args:**
 
 - <b>`start_date`</b> (str):  Start date in ISO8601 format. 
 - <b>`end_date`</b> (str):  End date in ISO8601 format. 
 - <b>`to_pandas`</b> (bool, optional):  If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  If True, enables cache. Defaults to True. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  History of recommended wallet. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_recommended_wallet_by_month`

```python
get_recommended_wallet_by_month(
    month: int,
    year: int,
    to_pandas: bool = True,
    enable_cache: bool = True
) → DataFrame
```

Get recommended wallet for a given month and year. 



**Args:**
 
 - <b>`month`</b> (int):  Month. 
 - <b>`year`</b> (int):  Year. 
 - <b>`to_pandas`</b> (bool, optional):  If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  If True, enables cache. Defaults to True. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  Recommended wallet for a given month and year. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_wallets_from_institutions`

```python
get_wallets_from_institutions(
    start_date: str,
    end_date: str,
    to_pandas: bool = True,
    enable_cache: bool = True
)
```

Get wallets from institutions. 



**Args:**
 
 - <b>`start_date`</b> (str):  Start date in ISO8601 format. 
 - <b>`end_date`</b> (str):  End date in ISO8601 format. 
 - <b>`to_pandas`</b> (bool, optional):  If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  If True, enables cache. Defaults to True. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  History of wallets from institutions. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/valor.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_wallets_from_institutions_by_month`

```python
get_wallets_from_institutions_by_month(
    month: int,
    year: int,
    to_pandas: bool = True,
    enable_cache: bool = True
) → DataFrame
```

Get wallets from institutions for a given month and year. 



**Args:**
 
 - <b>`month`</b> (int):  Month. 
 - <b>`year`</b> (int):  Year. 
 - <b>`to_pandas`</b> (bool, optional):  If True, returns a pandas.DataFrame. Otherwise, returns a list of dicts. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  If True, enables cache. Defaults to True. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  Wallets from institutions for a given month and year. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
