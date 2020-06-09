# Used for getting the list of associated companies/subsidiaries

import redis

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities


name = "associatesDetails"

report_types = [name]

scraper_api_key = constants.SCRAPER_API_KEY

ticker_report_page_count_key = f'{name}:trp_count'
ticker_report_page_crawled_key = f'{name}:trp_crawled'

crawled_set_key = f'{name}:{constants.CRAWLED_SET_SUFFIX}'
error_set_key = f'{name}:{constants.ERROR_SET_SUFFIX}'


ass = {"url": "https://finance.vietstock.vn/data/associatesdetails",
        "formdata": {
        "code": "",                          # ticker
        "page": constants.START_PAGE,        # loop until end page
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies":  {
            "language": constants.LANGUAGE,
        },
        "meta": {
            "ticker": "",
            "ReportType": "",
            "Page": "",
        },
        "proxies": {
            "http": constants.REQUESTS_LOCAL_PROXY,
            "https": constants.REQUESTS_LOCAL_PROXY,
        }
        }

log_settings = utilities.log_settings(spiderName=name,
                                      log_level="INFO",
                                      log_formatter="fad_crawl.spiders.models.utilities.TickerSpiderLogFormatter"
                                      )

middlewares_settings = {
    'DOWNLOADER_MIDDLEWARES': {
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        'fad_crawl.middlewares.TickerCrawlDownloaderMiddleware': 901,
        'fad_crawl.fad_stats.TickerCrawlerStats': 850,
        'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    },
    'SPIDER_MIDDLEWARES': {
        'fad_crawl.middlewares.TickerCrawlSpiderMiddleware': 45
    }
}

proxy_settings = {
    'ROTATING_PROXY_LIST': constants.PRIVOXY_LOCAL_PROXY,
}

redis_key_settings = {"REDIS_START_URLS_KEY": "%(name)s:tickers"}

settings = {**log_settings, **middlewares_settings, **proxy_settings, ** redis_key_settings}
