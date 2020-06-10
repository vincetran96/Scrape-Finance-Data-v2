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
from fad_crawl.spiders.models.corporateaz import name, settings, tickers_redis_keys, closed_redis_key
from fad_crawl.spiders.pdfDocs import pdfDocsHandler


TEST_TICKERS_LIST = ["AAA", "A32", "VIC"]
TEST_NUM_PAGES = 2


class corporateazHandler(scrapy.Spider):
    name = name
    custom_settings = settings

    def __init__(self, tickers_list="", *args, **kwargs):
        super(corporateazHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis()
        self.r.set(closed_redis_key, "0")

    def start_requests(self):
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
        tickers_list = [d["Code"] for d in res][:5] # FOR TESTING PURPOSE
        self.logger.info(str(tickers_list))
        print(str(tickers_list))
        
# Push the value ticker;1 to financeInfo to initiate its requests
        financeInfo_tickers = [f'{t};1' for t in tickers_list]
        self.r.lpush(tickers_redis_keys[0], *financeInfo_tickers)
        self.logger.info(financeInfo_tickers)
        print(financeInfo_tickers)

# Push the tickers list to Redis key of other Spiders
        for k in tickers_redis_keys[1:]:
            self.r.lpush(k, *tickers_list)

    def closed(self, reason="CorporateAZ Finished"):
        self.r.set(closed_redis_key, "1")
        self.logger.info(self.r.get(closed_redis_key))
