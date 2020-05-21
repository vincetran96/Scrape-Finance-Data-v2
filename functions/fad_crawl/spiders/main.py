# -*- coding: utf-8 -*-
# This spider crawls the list of company names on Vietstock

import scrapy
import json
import requests
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from financeInfo import financeInfoHandler
from models.corporateaz import data as az
import models.constants as constants


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
            print(az["cookies"])
            req = FormRequest(url=az["url"],
                              formdata=az["formdata"],
                              headers=az["headers"],
                              cookies=az["cookies"],
                              callback=self.parse)
            yield req

    def parse(self, response):
        # Load response to JSON
        res = json.loads(response.text)

        process = CrawlerProcess()
        process.crawl(financeInfoHandler, tickers_list=[i["Code"] for i in res])
        process.start()


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(corporateazHandler)
    process.start()
