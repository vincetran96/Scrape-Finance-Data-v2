
# This module contains settings for pdfDocs Spider

# Parameters for type are as follows
# 1: bao cao tai chinh
# 23: nghi quyet hoi dong quan tri
# 8: giai trinh ket qua kinh doanh
# 9: bao cao quan tri
# 2: bao cao thuong nien (cai nay rat nang ve content/graphics)
# 4: nghi quyet dai hoi co dong
# 5: tai lieu dai hoi co dong (file rar/zip)
# 3: ban cao bach
# 10: ty le von kha dung
# 6: tai lieu khac

import scraper_vietstock.spiders.models.constants as constants
import scraper_vietstock.spiders.models.utilities as utilities


name = "pdfDocs"

report_types = ["1", "23", "8", "9", "2", "4", "5", "3", "10", "6"]

data = {"url": "https://finance.vietstock.vn/data/getdocument",
        "formdata": {
            "code": "",  # ticker
            "type": "",  # document type, see above
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        },
        "meta": {
            "ticker": "",     # ticker
            "ReportType": ""  # document type, use this so we can use TickerCrawlSpiderMiddleware
        }
        }

log_settings = utilities.log_settings(spiderName=name,
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
    }
}

proxy_settings = {
    'ROTATING_PROXY_LIST': constants.PRIVOXY_LOCAL_PROXY,
}

redis_key_settings = {"REDIS_START_URLS_KEY": "%(name)s:corpAZtickers"}

file_settings = {
    'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},
    'FILES_STORE': 'LocalData/PDFs',
    'FILES_URLS_FIELD': 'file_urls',
    'FILES_RESULT_FIELD': 'files'
}

settings = {**log_settings, **middlewares_settings, **proxy_settings, ** redis_key_settings, **file_settings}
