# Used for getting the list of companies in the same industry

import redis

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities


name = "counterParts"

count_data = {"url": "https://finance.vietstock.vn/company/GetCountCompanyRelation",
              "formdata": {
                  "code": "",  # ticker
                  "tradingdate": "",  # YYYY-MM-DD
                  "exchangeID": ""
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
                  "counted": "",
                  "ReportType": "",
              }
              }

find_data = {"url": "https://finance.vietstock.vn/company/GetCompanyRelationFilter",
             "formdata": {
                 "code": "",  # ticker
                 "Page": constants.START_PAGE,
                 "PageSize": "",  # can be equal to result of the count above
                 "ToDate": "",  # YYYY-MM-DD
                 "ExchangeID": "",
                 "OrderBy": "0",
                 "Direction": ""
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
                 "counted": "",
                 "ReportType": "",
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

settings = {**log_settings, **middlewares_settings,
            **proxy_settings, ** redis_key_settings}
