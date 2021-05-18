# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's associated companies/subsidiaries

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

import scraper_vietstock.spiders.models.utilities as utilities
from scraper_vietstock.helpers.fileDownloader import save_jsonfile
from scraper_vietstock.spiders.fadRedis import fadRedisSpider
from scraper_vietstock.spiders.models.associatesdetails import data as ass
from scraper_vietstock.spiders.models.associatesdetails import name, settings


class associatesHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(associatesHandler, self).__init__(*args, **kwargs)
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

            # If page param. is pushed in, crawl that page
            # Otherwise begin with page 1
            try:
                page = params[1]
                req = self.make_request_from_data(ticker, page)
                if req:
                    yield req
                else:
                    self.logger.info(
                        "Request not made from params: %r", d)
            except:
                req = self.make_request_from_data(ticker, "1")
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
            self.close_status()

    def make_request_from_data(self, ticker, page):
        """
        Replaces the default method
        """

        ass["formdata"]["code"] = ticker
        ass["formdata"]["page"] = page
        ass["meta"]["ticker"] = ticker
        ass["meta"]["page"] = page

        return FormRequest(url=ass["url"],
                           formdata=ass["formdata"],
                           headers=ass["headers"],
                           cookies=ass["cookies"],
                           meta=ass["meta"],
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

                # If the current page < total page, push the next page to Redis q
                total_page = int(resp_json[0]['TotalPage'])
                if int(page) < total_page:
                    next_page = int(page) + 1
                    self.r.lpush(f'{self.name}:tickers',
                                 f'{ticker};{next_page}')
                
                # Saving local data files
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_Page_{page}.json')
                
                # ES push task
                handleES_task.delay(self.name.lower(), ticker, resp_json)

                self.r.srem(self.error_set_key,
                            f'{ticker};{page};{report_type}')
            except:
                self.logger.info("Response is an empty string")
                self.r.sadd(self.error_set_key,
                            f'{ticker};{page};{report_type}')
