# Used for getting the list of major shareholders of a company

import redis

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities

r = redis.Redis(decode_responses=True)

name = "majorshareholders"

scraper_api_key = constants.SCRAPER_API_KEY

data = {"url": "https://finance.vietstock.vn/data/shareholderdetails",
        "formdata": {
            "code": "", # ticker
            "page": constants.START_PAGE # loop until response == null
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies":  {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        },
        "meta": {
            "ticker": "",
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
    # 'ROTATING_PROXY_LIST': r.lrange(constants.PROXIES_REDIS_KEY, 0, -1),
    # 'ROTATING_PROXY_LIST': [constants.PRIVOXY_LOCAL_PROXY],
}

redis_key_settings = {"REDIS_START_URLS_KEY": "%(name)s:tickers"}

settings = {**log_settings, **middlewares_settings, **proxy_settings, ** redis_key_settings}
