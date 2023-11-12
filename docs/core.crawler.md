<!-- markdownlint-disable -->

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `core.crawler`






---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Crawler`
Base class for crawlers. 

If you want to create a new crawler, you should inherit from this class. It provides some useful methods for crawling. 



**Args:**
 
 - <b>`url`</b> (str):  Base url for the crawler. 

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(url: str)
```








---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_page`

```python
get_page(url: str = None, path: str = <class 'str'>, **kwargs) → str
```

Get a page from a given url. This is just a wrapper around `get_response` method. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_page_soup`

```python
get_page_soup(
    url: str = None,
    enable_cache: bool = True,
    **kwargs
) → BeautifulSoup
```

Get a BeautifulSoup object from a given url. This is just a wrapper around `get_page` method. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_response`

```python
get_response(url: str = None, path: str = <class 'str'>, **kwargs) → Response
```

Get a response from a given url. 



**Args:**
 
 - <b>`url`</b> (str, optional):  Url to get response from. Defaults to None. 
 - <b>`path`</b> (str, optional):  Path to join with base url. Defaults to str. 
 - <b>`kwargs`</b>:  Keyword arguments to pass to `requests.get`. 



**Returns:**
 
 - <b>`requests.Response`</b>:  Response from the given url. 

---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/crawler.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `join_url`

```python
join_url(*args: str) → str
```

Join url parts. 



**Args:**
 
 - <b>`*args (str)`</b>:  Url parts. 



**Returns:**
 
 - <b>`str`</b>:  Joined url. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
