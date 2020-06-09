# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's associated companies/subsidiaries

import json
import logging
import os
import sys
import traceback

import requests
import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str
from scrapy_redis.spiders import RedisSpider

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.associatesdetails import *
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key


class associatesHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(associatesHandler, self).__init__(*args, **kwargs)
        self.ass = ass
        self.report_types = report_types
        self.ticker_report_page_count_key = ticker_report_page_count_key
        self.crawled_set_key = crawled_set_key
        self.error_set_key = error_set_key

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
# Fetch one ticker from Redis list, mark all reports for this ticker as unfinished
            d = fetch_one(self.redis_key)
            if not d:
                break
            ticker = bytes_to_str(d, self.redis_encoding)
            self.ass["formdata"]["code"] = ticker
            for report_type in self.report_types:
# Look for number of pages for this ticker first
                try:
                    numPages = requests.post(url=self.ass["url"],
                                             data=self.ass["formdata"],
                                             headers=self.ass["headers"],
                                             cookies=self.ass["cookies"],
                                             proxies=self.ass["proxies"],
                                             verify=False
                                             ).json()[0]["TotalPage"]
                    self.logger.info(f'NumPages was calculated as {numPages}')
# If request above is not possible, assume numPages = 4
                except:
                    numPages = 4
                    self.logger.info(f'NumPages was assumed to be {numPages}')
# Increase the pages supposed to crawl by NumPages
                self.r.incr(self.ticker_report_page_count_key, numPages)
                self.logger.info(f'Total supposed to process: {self.r.get(self.ticker_report_page_count_key)}')
# Loop through all the pages
                for pg in range(1, numPages+1):
                    req = self.make_request_from_data(
                        ticker, report_type, page=str(pg))
                    if req:
                        yield req
                        # found += 1
                    else:
                        self.logger.info(
                            "Request not made from data: %r", d)
            found += 1
# Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)
# Close spider if corpAZ is closed and total processed == total supposed to process
# Total processed equals to # of values in crawled set plus values in error set
        total_processed = self.r.scard(self.crawled_set_key) + self.r.scard(self.error_set_key)

        if self.r.get(corpAZ_closed_key) == "1" and int(self.r.get(self.ticker_report_page_count_key)) == total_processed:
            self.logger.info(self.r.smembers(self.crawled_set_key))
            self.logger.info(self.r.smembers(self.error_set_key))
            
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed. Processed everything")

    def make_request_from_data(self, ticker, report_type, page):
        """
        Replaces the default method, data is a ticker.
        """

        self.ass["formdata"]["code"] = ticker
        self.ass["formdata"]["page"] = page
        self.ass["meta"]["ticker"] = ticker
        self.ass["meta"]["ReportType"] = report_type
        self.ass["meta"]["Page"] = page

        return FormRequest(url=self.ass["url"],
                           formdata=self.ass["formdata"],
                           headers=self.ass["headers"],
                           cookies=self.ass["cookies"],
                           meta=self.ass["meta"],
                           callback=self.parse,
                           errback=self.handle_error
                           )

    def parse(self, response):
        if response:
# If response is not an empty string, save it and +1 for # of pages crawled
            try:
                resp_json = json.loads(response.text)
                ticker = response.meta['ticker']
                report_type = response.meta['ReportType']
                page = response.meta['Page']
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_Page_{page}.json')
# Remove and add the value {ticker};{report_type};{page} accordingly
                self.r.srem(self.error_set_key, f'{ticker};{report_type};{page}')
                self.r.sadd(self.crawled_set_key, f'{ticker};{report_type};{page}')
            except:
                self.logger.info("Response is an empty string")

    def handle_error(self, failure):
        if failure.request:
            request = failure.request
            ticker = request.meta['ticker']
            report_type = request.meta['ReportType']
            page = request.meta['Page']
            self.logger.info(f'=== ERRBACK: on request for ticker {ticker}, report {report_type}, on page {page}')
            self.r.sadd(self.error_set_key, f'{ticker};{report_type};{page}')
        elif failure.value.response:
            response = failure.value.response
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['Page']
            self.logger.info(f'=== ERRBACK: on response for ticker {ticker}, report {report_type}, on page {page}')
            self.r.sadd(self.error_set_key, f'{ticker};{report_type};{page}')
