# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's associated companies/subsidiaries

import json
import logging
import os
import sys
import traceback

import redis
import requests
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
from fad_crawl.spiders.models.associatesdetails import *
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key


class associatesHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(associatesHandler, self).__init__(*args, **kwargs)
        self.ass = ass
        self.report_types = report_types
        self.idling = False

        self.ticker_report_page_count_key = ticker_report_page_count_key
        self.error_set_key = error_set_key

        self.r.set(self.ticker_report_page_count_key, "0")

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        This method customized from fadRedis Spider because it has the Page param. in formdata.
        """
        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            d = fetch_one(self.redis_key)
            if not d:
                break
            ticker = bytes_to_str(d, self.redis_encoding)
            self.ass["formdata"]["code"] = ticker
            self.idling = False
            for report_type in self.report_types:
                ## Look for number of pages for this ticker first
                ## If request above is not possible, assume numPages = 4
                ## Then increase the pages supposed to crawl by NumPages
                try:
                    numPages = requests.post(url=self.ass["url"],
                                             data=self.ass["formdata"],
                                             headers=self.ass["headers"],
                                             cookies=self.ass["cookies"],
                                             proxies=self.ass["proxies"],
                                             verify=False
                                             ).json()[0]["TotalPage"]
                    self.logger.info(
                        f'NumPages of report {report_type} for ticker {ticker} was calculated as {numPages}')
                except:
                    numPages = 4
                    self.logger.info(
                        f'NumPages of report {report_type} for ticker {ticker} was assumed to be {numPages}')

                self.r.incr(self.ticker_report_page_count_key, numPages)

                for pg in range(1, numPages+1):
                    req = self.make_request_from_data(
                        ticker, report_type, page=str(pg))
                    if req:
                        yield req
                    else:
                        self.logger.info(
                            "Request not made from data: %r", d)
            found += 1
        
        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)
        self.logger.info(
                    f'Total requests supposed to process: {self.r.get(self.ticker_report_page_count_key)}')

        ## Close spider if corpAZ is closed and none in queue and spider is idling
        ## Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Processed everything")

    def make_request_from_data(self, ticker, report_type, page):
        """
        Replaces the default method, adds report type and page
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

    def spider_idle(self):
        """Overwrites default method
        """
        self.idling = True
        self.schedule_next_requests()
        raise DontCloseSpider

    def parse(self, response):
        """
        If response is not an empty string, save it
        Then remove the value {ticker};{page};{report_type} from error set
        """
        if response:
            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                ticker = response.meta['ticker']
                report_type = response.meta['ReportType']
                page = response.meta['Page']
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_Page_{page}.json')
                self.r.srem(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                self.logger.info("Response is an empty string")

    def handle_error(self, failure):
        """
        If there's an error with a request/response, add it to the error set
        """
        if failure.request:
            request = failure.request
            ticker = request.meta['ticker']
            report_type = request.meta['ReportType']
            page = request.meta['Page']
            self.logger.info(
                f'=== ERRBACK: on request for ticker {ticker}, report {report_type}, on page {page}')
            self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type}')
        elif failure.value.response:
            response = failure.value.response
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['Page']
            self.logger.info(
                f'=== ERRBACK: on response for ticker {ticker}, report {report_type}, on page {page}')
            self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type}')
