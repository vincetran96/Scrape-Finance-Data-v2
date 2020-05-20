# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's balance sheet on Vietstock

import scrapy
import json
from scrapy import FormRequest
from pprint import pprint

LANGUAGE = "en-US"
USER_COOKIE = "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2\
    FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB\
    94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBE\
    DE986E6558A3C0BA"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/201001\
    01 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"


class VSTickerSpider(scrapy.Spider):
    name = 'BS_VS'

    def __init__(self, tickers_list="", **kwargs):
        self.tickers = tickers_list.split(",")
        super().__init__(**kwargs)

    def start_requests(self):
        for ticker in self.tickers:

            # TODO: Find out a more elegant way to crawl all pages of balance \
            # sheet, instead of passing PageSize = an arbitrarily large number

            # Currently testing making BS and IS spiders spawning from \
            # CrawlerProcess() in tickers_list module

            req_bs = FormRequest(url="https://finance.vietstock.vn/data/financeinfo",
                                 formdata={
                                     "Code": ticker,
                                     "ReportType": "CDKT",
                                     "ReportTermType": "2",
                                     "Unit": "1000000",
                                     "Page": "1",
                                     "PageSize": "999999999"
                                 },
                                 headers={
                                     "User-Agent": USER_AGENT,
                                     "Content-Type": CONTENT_TYPE
                                 },
                                 cookies={
                                     "language": LANGUAGE,
                                     "vts_usr_lg": USER_COOKIE
                                 },
                                 meta={
                                     'ticker': ticker,
                                     'ReportType': "CDKT"
                                 })
            yield req_bs

            req_is = FormRequest(url="https://finance.vietstock.vn/data/financeinfo",
                                 formdata={
                                     "Code": ticker,
                                     "ReportType": "KQKD",
                                     "ReportTermType": "2",
                                     "Unit": "1000000",
                                     "Page": "1",
                                     "PageSize": "999999999"
                                 },
                                 headers={
                                     "User-Agent": USER_AGENT,
                                     "Content-Type": CONTENT_TYPE
                                 },
                                 cookies={
                                     "language": LANGUAGE,
                                     "vts_usr_lg": USER_COOKIE
                                 },
                                 meta={
                                     'ticker': ticker,
                                     'ReportType': "KQKD"
                                 })
            yield req_is

    def parse(self, response):
        
        # TODO: add UTF-8 for Vietnamese text
        
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        with open(f'BS_VS_TEST/{ticker}_{report_type}.json', 'w') as writefile:
            json.dump(resp_json, writefile, indent=4)
        # Time period info
        # pprint(resp_json[0])
        # Balance sheet info
        # pprint(resp_json[1]["Balance Sheet"])
