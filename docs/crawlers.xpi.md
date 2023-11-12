<!-- markdownlint-disable -->

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/xpi.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `crawlers.xpi`






---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/xpi.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `XPICrawler`
Crawler for XP Investimentos. 



**Examples:**
 

```python
import brdata
crawler = brdata.XPICrawler()
crawler.get_analysis("PETR4")
``` 

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/xpi.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```








---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/crawlers/xpi.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_analysis`

```python
get_analysis(
    code: str,
    to_pandas: bool = True,
    enable_cache: bool = True,
    **kwargs
) → Series
```

Get stock analysis from XP Investimentos. 



**Args:**
 
 - <b>`code`</b> (str):  Stock code. 
 - <b>`to_pandas`</b> (bool, optional):  Whether to return a pandas.Series or a dict. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  Whether to enable cache. Defaults to True. 



**Raises:**
 
 - <b>`exceptions.NotFoundException`</b>:  Stock not found. 



**Returns:**
 
 - <b>`pd.Series`</b>:  Stock analysis. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
