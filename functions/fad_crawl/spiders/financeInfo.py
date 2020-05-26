# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's balance sheet on Vietstock

import json
import logging
import os
import sys
import traceback
from pprint import pprint

import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import functions.fad_crawl.spiders.models.utilities as utilities
from functions.fad_crawl.spiders.models.financeinfo import data as fi


class financeInfoHandler(scrapy.Spider):
    name = 'financeInfo'
    
    # Custom settings for spider
    log_settings = utilities.log_settings(spiderName=name, 
                                            log_level="INFO" ,
                                            log_formatter="functions.fad_crawl.spiders.models.utilities.TickerSpiderLogFormatter"
                                            )
    middlewares_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'functions.fad_crawl.middlewares.FadCrawlDownloaderMiddleware': 901,
            'functions.fad_crawl.fad_stats.TickerCrawlerStats': 850,
            'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
        },
        'SPIDER_MIDDLEWARES': {
            'functions.fad_crawl.middlewares.FadCrawlSpiderMiddleware': 45 #needs more research on this number...
        }
    }
    custom_settings = {**log_settings, **middlewares_settings}

    def __init__(self, tickers_list="", **kwargs):
        self.tickers = tickers_list

    def start_requests(self):
        for ticker in self.tickers:

# TODO: find out a more elegant way to crawl all pages of balance \
# sheet, instead of passing PageSize = an arbitrarily large number

            # try:
            fi["formdata"]["Code"] = ticker
            fi["formdata"]["ReportType"] = "CDKT"
            fi["meta"]["ReportType"] = "CDKT"
            fi["meta"]["ticker"] = ticker

            req_bs = FormRequest(url=fi["url"],
                                formdata=fi["formdata"],
                                headers=fi["headers"],
                                cookies=fi["cookies"],
                                meta=fi["meta"],
                                )
            yield req_bs

            fi["formdata"]["ReportType"] = "KQKD"
            fi["meta"]["ReportType"] = "KQKD"

            req_is = FormRequest(url=fi["url"],
                                formdata=fi["formdata"],
                                headers=fi["headers"],
                                cookies=fi["cookies"],
                                meta=fi["meta"],
                                )
            yield req_is
            # except:
            #     utilities.handle_exception(self, request_list = [req_bs, req_is])

# TODO: do we need to create a new parse function for each type of \
# financial report?
    
    def parse(self, response):

# TODO: add UTF-8 for Vietnamese text

        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'localData/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)


# if __name__ == "__main__":
#     process = CrawlerProcess()
#     process.crawl(financeInfoHandler)
#     process.start()
