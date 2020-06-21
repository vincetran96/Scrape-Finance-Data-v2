# -*- coding: utf-8 -*-
# This spider crawls the list of company names (tickers) on Vietstock,
# feeds the list to the Redis server for other Spiders to crawl

import json
import logging
import os
import sys
import traceback

import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy_redis.spiders import RedisSpider
from twisted.internet import reactor

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.corporateaz import closed_redis_key
from fad_crawl.spiders.models.corporateaz import data as az
from fad_crawl.spiders.models.corporateaz import (name, settings,
                                                  tickers_redis_keys)
from fad_crawl.spiders.pdfDocs import pdfDocsHandler
from fad_crawl.spiders.models.constants import REDIS_HOST


TEST_TICKERS_LIST = ["AAA", "A32", "VIC"]
TEST_NUM_PAGES = 2


class corporateazHandler(scrapy.Spider):
    name = name
    custom_settings = settings

    def __init__(self, tickers_list="", *args, **kwargs):
        super(corporateazHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis(host=REDIS_HOST, decode_responses=True)
        self.r.set(closed_redis_key, "0")

    def start_requests(self):
        req = FormRequest(url=az["url"],
                          formdata=az["formdata"],
                          headers=az["headers"],
                          cookies=az["cookies"],
                          meta=az["meta"],
                          callback=self.parse,
                          errback=self.handle_error)
        yield req

    def parse(self, response):
        if response:
            page = int(response.meta['page'])
            total_pages = response.meta['TotalPages']
            try:
                res = json.loads(response.text)
                tickers_list = [d["Code"]
                                for d in res]
                self.logger.info(
                    f'Found these tickers on page {page}: {str(tickers_list)}')

                # For financeInfo
                # Push the value ticker;1 to financeInfo to initiate its requests
                financeInfo_tickers = [f'{t};1' for t in tickers_list]
                # FOR TESTING PURPOSE
                if self.r.llen(tickers_redis_keys[0]) <= 3:
                    self.r.lpush(tickers_redis_keys[0], *financeInfo_tickers)

                # For other FAD Spiders
                # Push the tickers list to Redis key of other Spiders
                for k in tickers_redis_keys[1:]:
                    # FOR TESTING PURPOSE
                    if self.r.llen(k) <= 3:
                        self.r.lpush(k, *tickers_list)

                # Total pages need to be calculated or delivered from previous request's meta
                # If current page < total pages, send next request
                total_pages = res[0]['TotalRecord'] // int(
                    constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages)

                if page < total_pages:
                    next_page = str(page + 1)
                    az["formdata"]["page"] = next_page
                    az["meta"]["page"] = next_page
                    az["meta"]["TotalPages"] = str(total_pages)
                    req_next = FormRequest(url=az["url"],
                                           formdata=az["formdata"],
                                           headers=az["headers"],
                                           cookies=az["cookies"],
                                           meta=az["meta"],
                                           callback=self.parse,
                                           errback=self.handle_error)
                    yield req_next
            except:
                self.logger.info("Response is invalid")

    def closed(self, reason="CorporateAZ Finished"):
        self.r.set(closed_redis_key, "1")
        self.logger.info(
            f'Closing... Setting closed signal value to {self.r.get(closed_redis_key)}')
        self.logger.info(
            f'Tickers have been pushed into {str(tickers_redis_keys)}')

    def handle_error(self, failure):
        pass
