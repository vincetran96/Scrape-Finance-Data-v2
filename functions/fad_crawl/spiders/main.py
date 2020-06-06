# -*- coding: utf-8 -*-
# This spider crawls the list of company names (tickers) on Vietstock,
# feeds the list to the Redis server for other Spiders to crawl

import json
import logging
import os
import sys
import traceback

import redis
import requests
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy_redis.spiders import RedisSpider
from twisted.internet import reactor

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.corporateaz import data as az
from fad_crawl.spiders.models.corporateaz import name, settings, tickers_redis_keys
from fad_crawl.spiders.pdfDocs import pdfDocsHandler


TEST_TICKERS_LIST = ["AAA", "A32", "VIC"]
TEST_NUM_PAGES = 5


class corporateazHandler(scrapy.Spider):
    name = name
    custom_settings = settings

    def __init__(self, tickers_list="", *args, **kwargs):
        super(corporateazHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis()

    def start_requests(self):
        self.logger.info(self.r.lrange(constants.PROXIES_REDIS_KEY, 0, -1))
        numTickers = requests.post(url=az["url"],
                                   data=az["formdata"],
                                   headers=az["headers"],
                                   cookies=az["cookies"],
                                   proxies=az["proxies"],
                                   verify=False
                                   ).json()[0]["TotalRecord"]

        # numPages = numTickers // int(constants.PAGE_SIZE) + 2
        numPages = TEST_NUM_PAGES

        for numPage in range(1, numPages):
            self.logger.info(f'=== PAGE NUMBER === {numPage}')
            az["formdata"]["page"] = str(numPage)
            az["meta"]["pageid"] = str(numPage)
            req = FormRequest(url=az["url"],
                              formdata=az["formdata"],
                              headers=az["headers"],
                              cookies=az["cookies"],
                              meta=az["meta"],
                              callback=self.parse)
            yield req

        self.logger.info("=== I HAVE GONE THROUGH ALL PAGES ===")

    def parse(self, response):
        res = json.loads(response.text)
        tickers_list = [d["Code"] for d in res]
        self.logger.info(str(tickers_list))
        
        # Push the tickers list to Redis key of each Spider
        for k in tickers_redis_keys:
            self.r.lpush(k, *tickers_list)
