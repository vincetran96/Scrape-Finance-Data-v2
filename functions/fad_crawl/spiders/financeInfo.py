# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's finance reports on Vietstock

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
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import name, report_types, settings


class financeInfoHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.report_types = report_types
        self.fi = fi

    def make_request_from_data(self, data, report_type):
        """Replaces the default method, data is a ticker.
        """

        ticker = bytes_to_str(data, self.redis_encoding)

        self.fi["formdata"]["Code"] = ticker
        self.fi["formdata"]["ReportType"] = report_type
        self.fi["meta"]["ticker"] = ticker
        self.fi["meta"]["ReportType"] = report_type

        return FormRequest(url=self.fi["url"],
                            formdata=self.fi["formdata"],
                            headers=self.fi["headers"],
                            cookies=self.fi["cookies"],
                            meta=self.fi["meta"],
                            callback=self.parse
                            )

# # TODO: find out a more elegant way to crawl all pages of balance \
# # sheet, instead of passing PageSize = an arbitrarily large number
    
    def parse(self, response):
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'localData/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)
            c = self.r.incr(self.crawled_count_key)
            self.logger.info(f'Crawled {c} ticker-reports so far')
