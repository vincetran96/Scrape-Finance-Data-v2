# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's balance sheet on Vietstock

import json
import logging
import os
import sys
import traceback

import scrapy
import redis
from scraper_api import ScraperAPIClient
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import (name, report_types,
                                                  scraper_api_key, settings)


class financeInfoHandler(RedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, tickers_list="", *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.tickers = tickers_list
        self.report_types = report_types
        self.r = redis.Redis()
        self.crawled_count_key = f'{self.name}:crawledcount'
        # self.client = ScraperAPIClient(scraper_api_key)

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
            for report_type in self.report_types:
                req = self.make_request_from_data(data, report_type)
                if req:
                    yield req
                    found += 1
                    c = self.r.incr(self.crawled_count_key)
                    self.logger.info(f'Crawled {c} ticker-reports so far')
                else:
                    self.logger.info("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

        if self.r.llen(self.redis_key) == 0 and self.r.get(self.crawled_count_key) is not None:
            self.r.delete(self.crawled_count_key)
            self.crawler.engine.close_spider(spider=self, reason="Queue is empty, the spider closes")

    def make_request_from_data(self, data, report_type):
        """
        Replaces the default method, data is a ticker.
        """
        ticker = bytes_to_str(data, self.redis_encoding)

        fi["formdata"]["Code"] = ticker
        fi["formdata"]["ReportType"] = report_type
        fi["meta"]["ticker"] = ticker
        fi["meta"]["ReportType"] = report_type

        return FormRequest(url=fi["url"],
                            formdata=fi["formdata"],
                            headers=fi["headers"],
                            cookies=fi["cookies"],
                            meta=fi["meta"],
                            )

# # TODO: find out a more elegant way to crawl all pages of balance \
# # sheet, instead of passing PageSize = an arbitrarily large number
    
    def parse(self, response):
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'localData/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)
