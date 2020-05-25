# -*- coding: utf-8 -*-
# This spider crawls the list of company names on Vietstock

import json
import logging
import os
import sys
import traceback

import requests
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

import functions.fad_crawl.spiders.models.constants as constants
import functions.fad_crawl.spiders.models.utilities as utilities
from functions.fad_crawl.spiders.financeInfo import financeInfoHandler
from functions.fad_crawl.spiders.models.corporateaz import data as az
from functions.fad_crawl.spiders.pdfDocs import pdfDocsHandler

TEST_TICKERS_LIST = ["AAA", "A32"]


class corporateazHandler(scrapy.Spider):
    name = 'corporateAZ'

    def start_requests(self):
        numTickers = requests.post(url=az["url"],
                                   data=az["formdata"],
                                   headers=az["headers"],
                                   cookies=az["cookies"]
                                   ).json()[0]["TotalRecord"]
        numPages = numTickers // int(constants.PAGE_SIZE) + 2
        for numPage in range(1, numPages):
            self.logger.info(f'=== PAGE NUMBER === {numPage}')
            az["formdata"]["page"] = str(numPage)
            # print(az["cookies"])
            req = FormRequest(url=az["url"],
                              formdata=az["formdata"],
                              headers=az["headers"],
                              cookies=az["cookies"],
                              callback=self.parse)
            yield req

    def parse(self, response):
        # Load response to JSON
        res = json.loads(response.text)
        
        # Start a CrawlerRunner for all tickers
        runner = CrawlerRunner()
        runner.crawl(financeInfoHandler, tickers_list=[d["Code"] for d in res])
        # runner.crawl(pdfDocsHandler, tickers_list=[d["Code"] for d in res])
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())


def crawl_main():
    configure_logging()
    runner_main = CrawlerRunner()
    runner_main.crawl(corporateazHandler)
    d_main = runner_main.join()
    d_main.addBoth(lambda _: reactor.stop())
    try:
        reactor.run()
    except:
        pass

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
