# -*- coding: utf-8 -*-
# This spider crawls a ticker's PDF Documents

import json
import os
import sys
import traceback
from pprint import pprint

import redis
import scrapy
from scrapy import FormRequest, Request
from scrapy.crawler import CrawlerRunner
from scrapy.loader import ItemLoader
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.helpers.fileDownloader as pdf
from fad_crawl.items import PDFDocItem
from fad_crawl.spiders.models.pdfdocs import data as fi
from fad_crawl.spiders.models.pdfdocs import name, settings, report_types
from fad_crawl.spiders.fadRedis import fadRedisSpider


class pdfDocsHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(pdfDocsHandler, self).__init__(*args, **kwargs)
        self.report_types = report_types
        self.fi = fi

    def make_request_from_data(self, data, report_type):
        """Replaces the default method, data is a ticker.
        """

        ticker = bytes_to_str(data, self.redis_encoding)

        self.fi["formdata"]["code"] = ticker
        self.fi["formdata"]["type"] = report_type
        self.fi["meta"]["ticker"] = ticker
        self.fi["meta"]["ReportType"] = report_type

        return FormRequest(url=self.fi["url"],
                            formdata=self.fi["formdata"],
                            headers=self.fi["headers"],
                            cookies=self.fi["cookies"],
                            meta=self.fi["meta"],
                            callback=self.parse
                            )

    def parse(self, response):
        resp_json = json.loads(response.text)
        doc_urls = [d['Url'] for d in resp_json]
        ticker = response.meta["ticker"]
        doc_type = response.meta["ReportType"]

        l = ItemLoader(item=PDFDocItem(), response=response)
        l.add_value('file_urls', doc_urls)

        c = self.r.incr(self.crawled_count_key)
        self.logger.info(f'Crawled {c} ticker-reports so far')

        return l.load_item()

        # for d in resp_json:
        #     doc_title = d["Title"]
        #     ticker = response.meta["ticker"]
        #     doc_type = response.meta["ReportType"]
            
        #     filepath = f'localData/PDFs/{ticker}_{doc_type}_{doc_title}_'            
        #     c = self.r.incr(self.crawled_count_key)
        #     self.logger.info(f'Crawled {c} ticker-reports so far')
