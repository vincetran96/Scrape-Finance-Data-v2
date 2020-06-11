# -*- coding: utf-8 -*-
# FAD Redis spider - the project's RedisSpiders should be based on this

import json
import logging
import os
import sys
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

from fad_crawl.spiders.models.constants import ERROR_SET_SUFFIX
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key


class fadRedisSpider(RedisSpider):
    """Base RedisSpider for other spiders in this project
    """

    def __init__(self, *args, **kwargs):
        super(fadRedisSpider, self).__init__(*args, **kwargs)
        self.r = redis.Redis(decode_responses=True)
        self.report_types = []
        self.fi = {}

        self.error_set_key = f'{self.name}:{ERROR_SET_SUFFIX}'
        self.corpAZ_closed_key = corpAZ_closed_key

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        """

        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            for report_type in self.report_types:
                req = self.make_request_from_data(data, report_type)
                if req:
                    yield req
                else:
                    self.logger.info("Request not made from data: %r", data)
            found += 1

        # Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)

        # Close spider if corpAZ is closed and none in queue and spider is idling
        # Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Processed everything")

    def spider_idle(self):
        """Overwrites default method
        """
        self.idling = True
        self.logger.info("=== IDLING... ===")
        self.schedule_next_requests()
        raise DontCloseSpider

    def handle_error(self, failure):
        """If there's an error with a request/response, add it to the error set
        """
        if failure.request:
            request = failure.request
            ticker = request.meta['ticker']
            report_type = request.meta['ReportType']
            try:
                page = request.meta['Page']
                self.logger.info(
                    f'=== ERRBACK: on request for ticker {ticker}, report {report_type}, on page {page}')
                self.r.sadd(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                self.logger.info(
                    f'=== ERRBACK: on request for ticker {ticker}, report {report_type}')
                self.r.sadd(self.error_set_key, f'{ticker};1;{report_type}')
        elif failure.value.response:
            response = failure.value.response
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            try:
                page = response.meta['Page']
                self.logger.info(
                    f'=== ERRBACK: on response for ticker {ticker}, report {report_type}, on page {page}')
                self.r.sadd(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                page = response.meta['Page']
                self.logger.info(
                    f'=== ERRBACK: on response for ticker {ticker}, report {report_type}')
                self.r.sadd(self.error_set_key, f'{ticker};1;{report_type}')
