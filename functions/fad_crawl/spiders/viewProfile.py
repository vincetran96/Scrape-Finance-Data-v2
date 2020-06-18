# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's company structure on Vietstock

import json
import logging
import os
import sys
import traceback
import re

import scrapy
import redis
from scrapy import FormRequest
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.viewprofile import data as vprf
from fad_crawl.spiders.models.viewprofile import (name, settings)
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.helpers.fileDownloader import save_textfile


class viewProfileHandlder(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(viewProfileHandlder, self).__init__(*args, **kwargs)
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
            params = bytes_to_str(d, self.redis_encoding).split(";")
            ticker = params[0]
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

        vprf["formdata"]["code"] = ticker
        vprf["meta"]["ticker"] = ticker

        return FormRequest(url=vprf["url"],
                           formdata=vprf["formdata"],
                           headers=vprf["headers"],
                           cookies=vprf["cookies"],
                           meta=vprf["meta"],
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
            final_t = ""
            try:
                for e in response.xpath("//div[contains(@class, 'headline')]"):
                    s_heading = "-".join(e.xpath("./descendant::*/text()").getall())
                    heading = re.sub(r'(?![- ])\W+',r' ', s_heading).strip()
                    s_details = "-".join(e.xpath("./following::table/descendant-or-self::*/text()").getall())
                    details = re.sub(r'(?![- ])\W+',r' ', s_details).strip()
                    final_t = final_t + heading + ";" + details + "="

                save_textfile(
                    final_t, filename=f'localData/{self.name}/{ticker}_Page_{page}.txt')
                self.r.srem(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                self.logger.info("Response is an empty string")
                self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type}')
