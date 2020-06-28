# -*- coding: utf-8 -*-
# Used to crawl the top 2 industry levels of a company

import json
import logging
import os
import sys
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
from fad_crawl.spiders.models.ctkhdetails import data as ctk
from fad_crawl.spiders.models.ctkhdetails import name, settings

# Import ES Supporting mudules
from es_task import *

class ctkhDetailsHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(ctkhDetailsHandler, self).__init__(*args, **kwargs)
        self.idling = False

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
            self.idling = False
            req = self.make_request_from_data(ticker)
            if req:
                yield req
            else:
                self.logger.info(
                    "Request not made from params: %r", d)
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

    def make_request_from_data(self, ticker):
        """
        Replaces the default method
        """

        ctk["formdata"]["Code"] = ticker
        ctk["meta"]["ticker"] = ticker

        return FormRequest(url=ctk["url"],
                           formdata=ctk["formdata"],
                           headers=ctk["headers"],
                           cookies=ctk["cookies"],
                           meta=ctk["meta"],
                           callback=self.parse,
                           errback=self.handle_error
                           )

    def parse(self, response):
        """If response is not an empty string, parse it
        """
        if response:
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['page']
            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                # # Saving local Data files
                # save_jsonfile(
                #     resp_json, filename=f'localData/{self.name}/{ticker}_Page_{page}.json')
                
                # ES push task
                handleES_task.delay(self.name.lower(), ticker, resp_json)

                self.r.srem(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                self.logger.info("Response is an empty string")
                self.r.sadd(self.error_set_key,
                            f'{ticker};{page};{report_type}')
