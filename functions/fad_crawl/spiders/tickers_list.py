# -*- coding: utf-8 -*-
# This spider crawls the list of company names on Vietstock

import scrapy
import json
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from fad_crawl.spiders.BS_VS import VSTickerSpider


LANGUAGE = "vi-VN"
USER_COOKIE = "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBEDE986E6558A3C0BA"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

CAT_ID = "0"
INDUSTRY_ID = "0"
START_PAGE = "1"
PAGE_SIZE = "50"
BUSINESSTYPE_ID = "0"


class ExampleSpider(scrapy.Spider):
    name = 'tickers_list'

    def start_requests(self):
        req_tl = FormRequest(url="https://finance.vietstock.vn/data/corporateaz",
                             formdata={
                                 "catID": CAT_ID,
                                 "industryID": INDUSTRY_ID,
                                 "page": START_PAGE,
                                 "pageSize": PAGE_SIZE,
                                 "type": "0",
                                 "code": "",
                                 "businessTypeID": BUSINESSTYPE_ID,
                                 "orderBy": "Code",
                                 "orderDir": "ASC"
                             },
                             headers={
                                 "User-Agent": USER_AGENT,
                                 "Content-Type": CONTENT_TYPE
                             },
                             cookies={
                                 "language": LANGUAGE,
                                 "vts_usr_lg": USER_COOKIE
                             },
                             callback=self.parse)
        yield req_tl

    def parse(self, response):        
        # Load response to JSON
        resp_j = json.loads(response.text)

        # Max no. of tickers
        num_tickers = resp_j[0]['TotalRecord']
        
        # Start next requests from page 2 to the last page
        for page_number in range(2, int(num_tickers/int(PAGE_SIZE))+2):
            self.logger.info(f'=== PAGE NUMBER === {page_number}')
            req = FormRequest(url="https://finance.vietstock.vn/data/corporateaz",
                              formdata={
                                  "catID": CAT_ID,
                                  "industryID": INDUSTRY_ID,
                                  "page": str(page_number),
                                  "pageSize": PAGE_SIZE,
                                  "type": "0",
                                  "code": "",
                                  "businessTypeID": BUSINESSTYPE_ID,
                                  "orderBy": "Code",
                                  "orderDir": "ASC"
                              },
                              headers={
                                  "User-Agent": USER_AGENT,
                                  "Content-Type": CONTENT_TYPE
                              },
                              cookies={
                                  "language": LANGUAGE,
                                  "vts_usr_lg": USER_COOKIE
                              },
                              callback=self.parse)
            yield (req)
        
        # Get the list of tickers on the page and create a CrawlerProcess
        page_tickers = ""
        for obj in resp_j:
            page_tickers = page_tickers + obj['Code'] + ","
        page_tickers = page_tickers[:-1]

        process = CrawlerProcess()
        process.crawl(VSTickerSpider, tickers_list=page_tickers)
        process.start()
