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
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import name, report_types, settings


class financeInfoHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.fi = fi
        self.report_types = report_types
        self.redis_batch_size = 16
        self.tickers_count_key = f'{self.name}:tickers_count'
        self.ticker_report_crawled_key = f'{self.name}:tr_crawled'

        self.r.set(self.tickers_count_key, "0")
        self.r.set(self.ticker_report_crawled_key, "0")

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from fadRedis Spider because it has the Page param. in formdata.
        """

        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
# Fetch one ticker from Redis list, mark all reports for this ticker as unfinished
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            found += 1
            params = bytes_to_str(data, self.redis_encoding).split(";")
            ticker = params[0]
            page = params[1]            

# If report type is pushed in, this will be a subsequent request from self.parse()
            try:
                report_type = params[2]
                req = self.make_request_from_data(ticker, report_type, page)
                if req:
                    yield req
# For each report type, begin with Page 1 of all report types. Initial requests of Spider.
            except:
                self.r.incr(self.tickers_count_key)

                self.logger.info(
                f'CONSUMED {self.r.get(self.tickers_count_key)} TICKERS SO FAR')

                for report_type in self.report_types:
                    req = self.make_request_from_data(
                        ticker, report_type, page)
                    if req:
                        yield req
                    else:
                        self.logger.info(
                            "Request not made from data: %r", data)

# Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)

# Close spider if corpAZ is closed and amount actually crawled == amount supposed to be crawled
        ticker_report_total = int(self.r.get(
            self.tickers_count_key))*len(self.report_types)
        ticker_report_crawled = int(self.r.get(self.ticker_report_crawled_key))

        self.logger.info(f'Total supposed to crawl: {ticker_report_total}')
        self.logger.info(f'Total crawled: {ticker_report_crawled}')

        if self.r.get(corpAZ_closed_key) == "1" and ticker_report_total == ticker_report_crawled:
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed, crawled everything")

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
                           callback=self.parse
                           )

    def parse(self, response):
        if response:
            resp_json = json.loads(response.text)
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['Page']

# If the first obj in response is empty, then we've finished the report type for this ticker
            if resp_json[0] == []:
                self.r.incr(self.ticker_report_crawled_key)

                self.logger.info(
                    f'DONE ALL PAGES OF {report_type} FOR TICKER {ticker}')
                self.logger.info(
                    f'CRAWLED {self.r.get(self.ticker_report_crawled_key)} TICKER-REPORTS SO FAR')

# If there's actual data in response, save JSON and crawl the next page
            else:
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_Page_{page}.json')

                next_page = str(int(page) + 1)
                self.r.lpush(f'{self.name}:tickers',
                             f'{ticker};{next_page};{report_type}')
