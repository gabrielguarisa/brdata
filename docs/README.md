<!-- markdownlint-disable -->

# API Overview

## Modules

- [`core`](./core.md#module-core)
- [`core.crawler`](./core.crawler.md#module-corecrawler)
- [`core.exceptions`](./core.exceptions.md#module-coreexceptions)
- [`core.req`](./core.req.md#module-corereq)
- [`crawlers`](./crawlers.md#module-crawlers)
- [`crawlers.cvm`](./crawlers.cvm.md#module-crawlerscvm)
- [`crawlers.valor`](./crawlers.valor.md#module-crawlersvalor)
- [`crawlers.xpi`](./crawlers.xpi.md#module-crawlersxpi)

## Classes

- [`crawler.Crawler`](./core.crawler.md#class-crawler): Base class for crawlers.
- [`exceptions.BaseException`](./core.exceptions.md#class-baseexception): Base exception for all brdata exceptions.
- [`exceptions.NotFoundException`](./core.exceptions.md#class-notfoundexception): Exception raised when some resource is not founds.
- [`exceptions.RequestException`](./core.exceptions.md#class-requestexception): Exception raised when the maximum number of retries is reached.
- [`cvm.CVMCrawler`](./crawlers.cvm.md#class-cvmcrawler): Crawler for CVM data.
- [`valor.ValorEconomicoCrawler`](./crawlers.valor.md#class-valoreconomicocrawler): Crawler for Valor Economico.
- [`xpi.XPICrawler`](./crawlers.xpi.md#class-xpicrawler): Crawler for XP Investimentos.

## Functions

- [`req.get_response_cached`](./core.req.md#function-get_response_cached): Returns a response from a given url.
- [`req.new_user_agent`](./core.req.md#function-new_user_agent): Returns a new random user agent.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
