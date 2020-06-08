# -*- coding: utf-8 -*-
# FAD Redis spider - the project's RedisSpiders should be based on this

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


class fadRedisSpider(RedisSpider):
    """Base RedisSpider for other spiders in this project
    """

    def __init__(self, *args, **kwargs):
        super(fadRedisSpider, self).__init__(*args, **kwargs)
        self.r = redis.Redis()
        self.report_types = []
        self.fi = {}
        # if name is not None:
        self.crawled_count_key = f'{self.name}:crawledcount'
        self.dequeued_count_key = f'{self.name}:dequeuedcount'

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        """

        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
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
                    found += 1
                    dq = self.r.incr(self.dequeued_count_key)
                    self.logger.info(f'Dequeued {dq} ticker-reports so far')
                else:
                    self.logger.info("Request not made from data: %r", data)

        # Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

        # Close spider if none in queue and amount crawled == amount dequeued
        if self.r.get(self.crawled_count_key) and self.r.get(self.dequeued_count_key):
            if self.r.llen(self.redis_key) == 0 and self.r.get(self.crawled_count_key) >= self.r.get(self.dequeued_count_key):
                self.r.delete(self.crawled_count_key)
                self.r.delete(self.dequeued_count_key)
                self.crawler.engine.close_spider(spider=self, reason="Queue is empty, the spider closes")
