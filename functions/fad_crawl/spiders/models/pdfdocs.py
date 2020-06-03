# -*- coding: utf-8 -*-
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

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities


name = "pdfDocs"

type_list = ["1", "23", "8", "9", "2", "4", "5", "3", "10", "6"]

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
            "ticker": "",
            "DocType": ""
        }
        }

log_settings = utilities.log_settings(spiderName=name,
                                      log_level="INFO",
                                      log_formatter="fad_crawl.spiders.models.utilities.TickerSpiderLogFormatter"
                                      )

middlewares_settings = {
    'DOWNLOADER_MIDDLEWARES': {
        # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        # 'fad_crawl.middlewares.TickerCrawlDownloaderMiddleware': 901,
        # 'fad_crawl.fad_stats.TickerCrawlerStats': 850,
        'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    },
    'SPIDER_MIDDLEWARES': {
        # 'fad_crawl.middlewares.TickerCrawlSpiderMiddleware': 45
    }
}

redis_key_settings = {"REDIS_START_URLS_KEY": "%(name)s:tickers"}

settings = {**log_settings, **middlewares_settings, ** redis_key_settings}
