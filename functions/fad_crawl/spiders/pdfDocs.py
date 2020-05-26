# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's PDF Documents

import json
import os
import sys
import traceback
from pprint import pprint

import scrapy
from scrapy import FormRequest, Request
from scrapy.crawler import CrawlerRunner

from fad_crawl.spiders.models.pdfdocs import data as fi
from fad_crawl.spiders.models.pdfdocs import type_list


class pdfDocsHandler(scrapy.Spider):
    name = 'pdfDocs'

    def __init__(self, tickers_list="", *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.tickers = tickers_list
    
    def start_requests(self):
        for ticker in self.tickers:
            for doc_type in type_list:
                fi["formdata"]["code"] = ticker
                fi["formdata"]["type"] = doc_type
                fi["meta"]["ticker"] = ticker
                fi["meta"]["DocType"] = doc_type

                req = FormRequest(url=fi["url"],
                                    formdata=fi["formdata"],
                                    headers=fi["headers"],
                                    cookies=fi["cookies"],
                                    meta=fi["meta"],
                                    callback=self.parse
                                    )
                yield req

    def parse(self, response):
        resp_json = json.loads(response.text)
        for d in resp_json:
            doc_req = Request(url=d["Url"], callback=self.parse_doc)
            doc_req.meta["DocTitle"] = d["Title"]
            doc_req.meta["FullTitle"] = d["FullName"]
            doc_req.meta["ticker"] = response.meta["ticker"]
            doc_req.meta["DocType"] = response.meta["DocType"]
            yield doc_req

# TODO: use another module for handling downloads of PDFs

    def parse_doc(self, response):
        ticker = response.meta["ticker"]
        doc_type = response.meta["DocType"]
        doc_title = response.meta["DocTitle"]

# TODO: how to download large documents using chunks?

        with open(f'localData/PDFs/{ticker}_{doc_type}_{doc_title}.pdf', 'wb') as writefile:
            writefile.write(response.body)


# if __name__ == "__main__":
#     runner = CrawlerRunner()
#     runner.crawl(pdfDocsHandler, tickers_list=TEST_TICKERS_LIST)
#     d = runner.join()
#     d.addBoth(lambda _: reactor.stop())
#     reactor.run()
