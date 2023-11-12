<!-- markdownlint-disable -->

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/cvm.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `crawlers.cvm`




**Global Variables**
---------------
- **VALID_PREFIXES**


---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/cvm.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CVMCrawler`
Crawler for CVM data. 



**Example:**
 

```python
import brdata
crawler = brdata.CVMCrawler()
crawler.get_documents("DFP", 2010, 2020)
``` 

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/cvm.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```








---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/cvm.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_documents`

```python
get_documents(
    prefix: str,
    start_year: str,
    end_year: str,
    enable_cache: bool = True
)
```

Get all documents for a given period. 



**Args:**
 
 - <b>`prefix`</b> (str):  One of the valid prefixes. See `VALID_PREFIXES`. 
 - <b>`start_year`</b> (str):  Year to start getting documents from. 
 - <b>`end_year`</b> (str):  Year to end getting documents from. 
 - <b>`enable_cache`</b> (bool, optional):  Whether to use cache or not. Defaults to True. 



**Raises:**
 
 - <b>`ValueError`</b>:  If prefix is not valid. 
 - <b>`ValueError`</b>:  If start_year is not valid. 
 - <b>`ValueError`</b>:  If end_year is not valid. 



**Returns:**
 
 - <b>`dict`</b>:  Dictionary of pandas.DataFrame with the documents. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/cvm.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_documents_by_year`

```python
get_documents_by_year(prefix: str, year: str, enable_cache: bool = True)
```

Get all documents for a given year. 



**Args:**
 
 - <b>`prefix`</b> (str):  One of the valid prefixes. See `VALID_PREFIXES`. 
 - <b>`year`</b> (str):  Year to get documents from. 
 - <b>`enable_cache`</b> (bool, optional):  Whether to use cache or not. Defaults to True. 



**Raises:**
 
 - <b>`ValueError`</b>:  If prefix is not valid. 
 - <b>`ValueError`</b>:  If year is not valid. 



**Returns:**
 
 - <b>`dict`</b>:  Dictionary of pandas.DataFrame with the documents. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
