# This module contains settings for financeInfo Spider
# Report types are summarized finances (BCTT), business targets (CTKH), balance sheets (CDKT),
# income statements (KQKD), cash flow statements (LC), and financial indices (CSTC)
# Report terms can be either "1" (for annual) or "2" (for quarter)

import scraper_vietstock.spiders.models.constants as constants
import scraper_vietstock.spiders.models.utilities as utilities


name = "financeInfo"

report_types = ["CTKH", "CDKT", "KQKD", "LC", "CSTC"]
report_terms = {"1":"Annual", "2":"Quarter"}

corpAZ_key = f'{name}:corpAZtickers'
scrape_key = f'{name}:scrape'
enqueued_key = f'{name}:enqueued'

data = {"url": "https://finance.vietstock.vn/data/financeinfo",
        "formdata": {
            "Code": "",
            "ReportType": "",
            "ReportTermType": "",
            "Unit": "1000000",
            "Page": constants.START_PAGE,
            "PageSize": "4",
            "__RequestVerificationToken": constants.REQ_VER_TOKEN_POST
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE,
        },
        "cookies": {
            "language": constants.LANGUAGE,
            "__RequestVerificationToken": constants.REQ_VER_TOKEN_COOKIE,
            "vts_usr_lg": constants.USER_COOKIE
        },
        "meta": {
            "ticker": "",
            "ReportType": "",
            "page": "",
            "ReportTermType": "",
        }
}

log_settings = utilities.log_settings(
    spiderName=name,
    log_level="INFO",
    log_formatter="scraper_vietstock.spiders.models.utilities.TickerSpiderLogFormatter"
)

middlewares_settings = {
    'DOWNLOADER_MIDDLEWARES': {
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        # 'scraper_vietstock.middlewares.TickerCrawlDownloaderMiddleware': 901,
        # 'scraper_vietstock.fad_stats.TickerCrawlerStats': 850,
        'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    },
    'SPIDER_MIDDLEWARES': {
        # 'scraper_vietstock.middlewares.TickerCrawlSpiderMiddleware': 45
    },
    'HTTPERROR_ALLOWED_CODES': []
}

proxy_settings = {
    'ROTATING_PROXY_LIST': constants.PRIVOXY_LOCAL_PROXY,
}

redis_settings = {
    # 'REDIS_START_URLS_KEY': "%(name)s:corpAZtickers",
    'REDIS_HOST': constants.REDIS_HOST,
    'REDIS_PORT': constants.REDIS_PORT
}

concurrency_settings = {
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 2.5,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 16,
    'DOWNLOAD_DELAY': 0.5
}

settings = {
    **log_settings,
    **middlewares_settings,
    **proxy_settings,
    ** redis_settings,
    **concurrency_settings
}
