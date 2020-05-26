# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's balance sheet on Vietstock

import json
import logging
import os
import sys
import traceback
from pprint import pprint

import scrapy
from scraper_api import ScraperAPIClient
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import scraper_api_key


class financeInfoHandler(RedisSpider):
    name = 'financeInfo'
    # start_urls = []
    
    # Custom settings for spider
    # log_settings = utilities.log_settings(spiderName=name, 
    #                                         log_level="INFO" ,
    #                                         log_formatter="fad_crawl.spiders.models.utilities.TickerSpiderLogFormatter"
    #                                         )
    # middlewares_settings = {
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'fad_crawl.middlewares.TickerCrawlDownloaderMiddleware': 901,
    #         'fad_crawl.fad_stats.TickerCrawlerStats': 850,
    #         'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    #     },
    #     'SPIDER_MIDDLEWARES': {
    #         'fad_crawl.middlewares.TickerCrawlSpiderMiddleware': 45 #needs more research on this number...
    #     }
    # }
    # custom_settings = {**log_settings, **middlewares_settings}
    custom_settings = {"REDIS_START_URLS_KEY": "%(name)s:tickers"}

    def __init__(self, tickers_list="", *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.tickers = tickers_list
        # self.client = ScraperAPIClient(scraper_api_key)

    def make_request_from_data(self, data):
        """Returns a Request instance from data coming from Redis.

        By default, ``data`` is an encoded URL. You can override this method to
        provide your own message decoding.

        Parameters
        ----------
        data : bytes
            Message from redis.
            In this case the ticker.

        """
        ticker = bytes_to_str(data, self.redis_encoding)
        
        fi["formdata"]["Code"] = ticker
        fi["formdata"]["ReportType"] = "CDKT"
        fi["meta"]["ticker"] = ticker
        fi["meta"]["ReportType"] = "CDKT"
        
        return FormRequest(url=fi["url"],
                            formdata=fi["formdata"],
                            headers=fi["headers"],
                            cookies=fi["cookies"],
                            meta=fi["meta"],
                            )

#     def start_requests(self):

# # TODO: find out a more elegant way to crawl all pages of balance \
# # sheet, instead of passing PageSize = an arbitrarily large number

#         # for ticker in self.tickers:
#         #     fi["formdata"]["Code"] = ticker
#         #     fi["formdata"]["ReportType"] = "CDKT"
#         #     fi["meta"]["ticker"] = ticker
#         #     fi["meta"]["ReportType"] = "CDKT"
            
#         #     req_bs = FormRequest(url=fi["url"],
#         #                         formdata=fi["formdata"],
#         #                         headers=fi["headers"],
#         #                         cookies=fi["cookies"],
#         #                         meta=fi["meta"],
#         #                         )
#         #     yield req_bs

#         for u in self.start_urls:
#             fi["formdata"]["Code"] = u
#             fi["formdata"]["ReportType"] = "CDKT"
#             fi["meta"]["ticker"] = u
#             fi["meta"]["ReportType"] = "CDKT"
            
#             req_bs = FormRequest(url=fi["url"],
#                                 formdata=fi["formdata"],
#                                 headers=fi["headers"],
#                                 cookies=fi["cookies"],
#                                 meta=fi["meta"],
#                                 )
#             yield req_bs
    
    def parse(self, response):
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'localData/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)
