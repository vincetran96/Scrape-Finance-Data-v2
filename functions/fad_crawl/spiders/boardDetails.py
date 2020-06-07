# -*- coding: utf-8 -*-
# Used for getting the list of the members of the board of directors of a company

import json
import logging
import os
import sys
import traceback

import scrapy
import redis
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import functions.fad_crawl.spiders.models.utilities as utilities
from functions.fad_crawl.spiders.models.boarddetails import data as bd
from functions.fad_crawl.spiders.models.boarddetails import (name,
                                                  scraper_api_key, settings)


class boardDetailsHandler(RedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(boardDetailsHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis()
        self.crawled_count_key = f'{self.name}:crawledcount'
        self.dequeued_count_key = f'{self.name}:dequeuedcount'

    def next_requests(self):
        """
        Replaces the default method. Closes spider when tickers are crawled and queue empty.
        """
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            req = self.make_request_from_data(data)
            if req:
                yield req
                found += 1
                dq = self.r.incr(self.dequeued_count_key)
                self.logger.info(f'Dequeued {dq} ticker-reports so far')
            else:
                self.logger.info("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

        # Close spider if none in queue and amount crawled == amount dequeued
        if self.r.get(self.crawled_count_key) and self.r.get(self.dequeued_count_key):
            if self.r.llen(self.redis_key) == 0 and self.r.get(self.crawled_count_key) >= self.r.get(self.dequeued_count_key):
                self.r.delete(self.crawled_count_key)
                self.r.delete(self.dequeued_count_key)
                self.crawler.engine.close_spider(spider=self, reason="Queue is empty, the spider closes")

    def make_request_from_data(self, data):
        """
        Replaces the default method, data is a ticker.
        """
        ticker = bytes_to_str(data, self.redis_encoding)

        bd["formdata"]["code"] = ticker
        bd["meta"]["ticker"] = ticker

        return FormRequest(url=bd["url"],
                            formdata=bd["formdata"],
                            headers=bd["headers"],
                            cookies=bd["cookies"],
                            meta=bd["meta"],
                            callback=self.parse
                            )

# # TODO: find out a more elegant way to crawl all pages of balance \
# # sheet, instead of passing PageSize = an arbitrarily large number
    
    def parse(self, response):
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        with open(f'localData/{name}/{ticker}_{name}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)
            c = self.r.incr(self.crawled_count_key)
            self.logger.info(f'Crawled {c} ticker-reports so far')
