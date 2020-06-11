# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's finance reports on Vietstock

import json
import logging
import os
import sys
import time
import traceback

import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DontCloseSpider
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key
from fad_crawl.spiders.models.financeinfo import *


class financeInfoHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.fi = fi
        self.report_types = report_types
        self.idling = False

        self.ticker_report_page_count_key = ticker_report_page_count_key
        self.r.set(self.ticker_report_page_count_key, "0")

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from fadRedis Spider because it has the Page param. in formdata.
        """

        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            params = bytes_to_str(data, self.redis_encoding).split(";")
            ticker = params[0]
            page = params[1]
            self.idling = False
            
            # If report type is pushed in, this will be a subsequent request from self.parse()
            # For each report type, begin with Page 1 of all report types. Initial requests of Spider.
            try:
                report_type = params[2]
                req = self.make_request_from_data(ticker, report_type, page)
                if req:
                    yield req
                    self.r.incr(self.ticker_report_page_count_key)
                else:
                    self.logger.info(
                        "Request not made from params: %r", params)
            except:
                for report_type in self.report_types:
                    req = self.make_request_from_data(
                        ticker, report_type, page)
                    if req:
                        yield req
                        self.r.incr(self.ticker_report_page_count_key)
                    else:
                        self.logger.info(
                            "Request not made from params: %r", params)
            found += 1

        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)
        self.logger.info(
            f'Total requests supposed to process: {self.r.get(self.ticker_report_page_count_key)}')
        
        # Close spider if corpAZ is closed and none in queue and spider is idling
        # Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Processed everything")

    def make_request_from_data(self, ticker, report_type, page):
        """Replaces the default method, data is a ticker.
        """
        self.fi["formdata"]["Code"] = ticker
        self.fi["formdata"]["ReportType"] = report_type
        self.fi["formdata"]["Page"] = page
        self.fi["meta"]["ticker"] = ticker
        self.fi["meta"]["ReportType"] = report_type
        self.fi["meta"]["Page"] = page

        return FormRequest(url=self.fi["url"],
                           formdata=self.fi["formdata"],
                           headers=self.fi["headers"],
                           cookies=self.fi["cookies"],
                           meta=self.fi["meta"],
                           callback=self.parse,
                           errback=self.handle_error
                           )

    def parse(self, response):
        """If the first obj in response is empty, then we've finished the report type for this ticker
        If there's actual data in response, save JSON and remove {ticker};{page};{report_type} value
        from error list, then crawl the next page
        """
        if response:
            resp_json = json.loads(response.text, encoding='utf-8')
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['Page']

            if resp_json[0] == []:
                self.logger.info(
                    f'DONE ALL PAGES OF {report_type} FOR TICKER {ticker}')
            else:
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_Page_{page}.json')
                self.r.srem(self.error_set_key,
                            f'{ticker};{page};{report_type}')
                next_page = str(int(page) + 1)
                self.r.lpush(f'{self.name}:tickers',
                             f'{ticker};{next_page};{report_type}')
