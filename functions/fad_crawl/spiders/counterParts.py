# -*- coding: utf-8 -*-
# Used for getting the list of companies in the same industry

import json
import logging
import os
import sys
import traceback
from datetime import date

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
from fad_crawl.spiders.models.counterparts import count_data
from fad_crawl.spiders.models.counterparts import find_data as ctp
from fad_crawl.spiders.models.counterparts import name, settings

# Import ES Supporting mudules
from es_task import *

class counterPartsHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(counterPartsHandler, self).__init__(*args, **kwargs)
        self.date = str(date.today().strftime("%Y-%m-%d"))
        self.idling = False

    def next_requests(self):
        """
        Replaces the default method. Closes spider when tickers are crawled and queue empty.
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
            self.idling = False
            try:
                pageSize = params[1]
                req = self.make_request_from_data(ticker, pageSize)
                if req:
                    yield req
                else:
                    self.logger.info("Request not made from data: %r", data)
            except:
                count_data["formdata"]["code"] = ticker
                count_data["formdata"]["tradingdate"] = self.date
                count_data["meta"]["ticker"] = ticker
                count_data["meta"]["counted"] = "0"
                req = FormRequest(url=count_data["url"],
                                  formdata=count_data["formdata"],
                                  headers=count_data["headers"],
                                  cookies=count_data["cookies"],
                                  meta=count_data["meta"],
                                  callback=self.parse,
                                  errback=self.handle_error
                                  )
                if req:
                    yield req
                    self.logger.info(
                        f'Counting number of associates of {ticker}')
                else:
                    self.logger.info("Request not made from data: %r", data)
            found += 1

        if found:
            self.logger.debug("Read %s params from '%s'",
                              found, self.redis_key)

        # Close spider if corpAZ is closed and none in queue and spider is idling
        # Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(self.corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Processed everything")

    def make_request_from_data(self, ticker, pageSize):
        """
        Replaces the default method, data is a ticker.
        """
        ctp["formdata"]["code"] = ticker
        ctp["formdata"]["PageSize"] = pageSize
        ctp["formdata"]["ToDate"] = self.date
        ctp["meta"]["ticker"] = ticker
        ctp["meta"]["counted"] = "1"

        return FormRequest(url=ctp["url"],
                           formdata=ctp["formdata"],
                           headers=ctp["headers"],
                           cookies=ctp["cookies"],
                           meta=ctp["meta"],
                           callback=self.parse,
                           errback=self.handle_error
                           )

    def parse(self, response):
        if response:
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['page']
            counted = int(response.meta['counted'])
            try:
                resp_json = json.loads(response.text,  encoding='utf-8')

                if counted == 0:
                    pageSize = int(resp_json) + 1
                    self.r.lpush(f'{self.name}:tickers', f'{ticker};{pageSize}')
                    self.logger.info(f'CRAWLING {pageSize} COUNTERPARTS OF {ticker}')
                else:
                    # # Saving local data files
                    # save_jsonfile(
                    #     resp_json, filename=f'localData/{self.name}/{ticker}_{self.name}.json')
                    
                    # ES push task
                    handleES_task.delay(self.name.lower(), ticker, resp_json)

                    self.r.srem(self.error_set_key,
                                f'{ticker};{page};{report_type}')
                    self.logger.info(f'CRAWLED COUNTERPARTS OF {ticker}')
            except:
                self.logger.info("Response is an empty string")
                self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type}')
