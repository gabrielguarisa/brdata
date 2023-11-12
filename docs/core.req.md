<!-- markdownlint-disable -->

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/req.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `core.req`





---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/brdata/core/req.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `new_user_agent`

```python
new_user_agent() → str
```

Returns a new random user agent. 


---

<a href="https://github.com/gabrielguarisa/brdata/blob/main/core/req/get_response_cached#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_response_cached`

```python
get_response_cached(
    url: str,
    max_retries: int = 5,
    timeout: int = 10,
    verify: bool = True
) → Response
```

Returns a response from a given url. 



**Args:**
 
 - <b>`url`</b> (str):  url to get response from. 
 - <b>`max_retries`</b> (int, optional):  Maximum number of retries. Defaults to 5. 
 - <b>`timeout`</b> (int, optional):  Timeout in seconds. Defaults to 10. 
 - <b>`verify`</b> (bool, optional):  Whether to verify SSL certificate. Defaults to True. 
 - <b>`enable_cache`</b> (bool, optional):  Whether to use cache or not. Defaults to True. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
