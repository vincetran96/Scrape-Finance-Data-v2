# -*- coding: utf-8 -*-
# This module contains settings for financeInfo Spider

# Report types are summarized finances (BCTT), business targets (CTKH), balance sheets (CDKT),
# income statements (KQKD), cash flow statements (LC), and financial indices (CSTC)

import redis

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities


name = "financeInfo"

report_types = ["BCTT", "CTKH", "CDKT", "KQKD", "LC", "CSTC"]

scraper_api_key = constants.SCRAPER_API_KEY

data = {"url": "https://finance.vietstock.vn/data/financeinfo",
        "formdata": {
            "Code": "",
            "ReportType": "",
            "ReportTermType": "2",
            "Unit": "1000000",
            "Page": constants.START_PAGE,
            "PageSize": "4",
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE,
        },
        "cookies": {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE,
        },
        "meta": {
            "ticker": "",
            "ReportType": "",
            "Page": constants.START_PAGE,
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

concurrency_settings = {'CONCURRENT_REQUESTS': 16}

settings = {**log_settings, **middlewares_settings, **proxy_settings, ** redis_key_settings, **concurrency_settings}
