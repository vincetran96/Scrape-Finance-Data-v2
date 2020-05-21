# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's balance sheet on Vietstock

import scrapy
import json
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from pprint import pprint
from models.financeinfo import data as fi


class financeInfoHandler(scrapy.Spider):
    name = 'financeInfo'

    def __init__(self, tickers_list="", **kwargs):
        self.tickers = tickers_list

    def start_requests(self):
        for ticker in self.tickers:

            # TODO: Find out a more elegant way to crawl all pages of balance \
            # sheet, instead of passing PageSize = an arbitrarily large number

            # Currently testing making BS and IS spiders spawning from \
            # CrawlerProcess() in tickers_list module
            fi["formdata"]["Code"] = ticker
            fi["meta"]["ticker"] = ticker
            fi["formdata"]["ReportType"] = "CDKT"
            fi["meta"]["ReportType"] = "CDKT"

            req_bs = FormRequest(url=fi["url"],
                                 formdata=fi["formdata"],
                                 headers=fi["headers"],
                                 cookies=fi["cookies"],
                                 meta=fi["meta"],
                                 )
            yield req_bs

            fi["formdata"]["ReportType"] = "KQKD"
            fi["meta"]["ReportType"] = "KQKD"
            
            req_is = FormRequest(url=fi["url"],
                                 formdata=fi["formdata"],
                                 headers=fi["headers"],
                                 cookies=fi["cookies"],
                                 meta=fi["meta"],
                                 )
            yield req_is

    def parse(self, response):

        # TODO: add UTF-8 for Vietnamese text

        resp_json = json.loads(response.text)

        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'localData/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(financeInfoHandler)
    process.start()
