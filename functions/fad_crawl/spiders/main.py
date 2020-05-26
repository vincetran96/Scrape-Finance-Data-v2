# -*- coding: utf-8 -*-
# This spider crawls the list of company names on Vietstock

import json
import logging
import os
import sys
import traceback

import redis
import requests
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy_redis.spiders import RedisSpider
from twisted.internet import reactor

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.models.corporateaz import data as az
from fad_crawl.spiders.pdfDocs import pdfDocsHandler

TEST_TICKERS_LIST = ["AAA", "A32", "VIC"]
TEST_NUM_PAGES = 40


class corporateazHandler(scrapy.Spider):
    name = 'corporateAZ'

    def __init__(self, tickers_list="", *args, **kwargs):
        super(corporateazHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis()

    def start_requests(self):
        numTickers = requests.post(url=az["url"],
                                   data=az["formdata"],
                                   headers=az["headers"],
                                   cookies=az["cookies"]
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

    def parse(self, response):
        res = json.loads(response.text)
        tickers_list = [d["Code"] for d in res]
        self.logger.info(str(tickers_list))
        self.r.lpush("financeInfo:tickers", *tickers_list)


def crawl_main():
    configure_logging()
    runner_main = CrawlerRunner()
    runner_main.crawl(corporateazHandler)
    d_main = runner_main.join()
    d_main.addBoth(lambda _: reactor.stop())
    reactor.run()


def crawl_test():
    runner_test = CrawlerRunner()
    runner_test.crawl(financeInfoHandler, tickers_list=TEST_TICKERS_LIST)
    # runner_test.crawl(pdfDocsHandler, tickers_list=TEST_TICKERS_LIST)
    d = runner_test.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    crawl_main()
    crawl_test()
