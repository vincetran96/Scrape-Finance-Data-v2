# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's finance reports on Vietstock

import json
import logging
import os
import sys
import time
import traceback

import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import name, report_types, settings


class financeInfoHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.fi = fi
        self.report_types = report_types
        self.redis_batch_size = 1

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from fadRedis Spider because it has the Page param. in formdata.
        """

        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
# Fetch one ticker from Redis list, mark all reports for this ticker as unfinished        
        while found < self.redis_batch_size:
            
# TODO: maybe delete the finished ticker Redis key here            
            
            data = fetch_one(self.redis_key)
            if not data:
                break
            
            found += 1
            ticker = bytes_to_str(data, self.redis_encoding)
            self.logger.info(f'=== Found ticker {ticker} ===')


            # for report_type in self.report_types:
            #     pg = 1
            #     req = self.make_request_from_data(ticker, report_type, page=str(pg))
            #     yield req
            #     dq = self.r.incr(self.dequeued_count_key)
            #     self.logger.info(f'Dequeued {dq} ticker-report-page so far')


# For each report type, begin while loop with Page number 1
            for report_type in self.report_types:
                self.r.hset(f'{self.name}:{ticker}:finished', report_type, "0")
                pg = 1
                while self.r.hget(f'{self.name}:{ticker}:finished', report_type) == "0":
                    req = self.make_request_from_data(ticker, report_type, page=str(pg))
                    if req:
                        yield req
                        dq = self.r.incr(self.dequeued_count_key)
                        self.logger.info(f'Dequeued {dq} ticker-report-page so far')
                        
                        
                        self.logger.info("inside while loop")
                        self.logger.info(self.r.hgetall(f'{self.name}:{ticker}:finished'))
                        print ("inside while loop: ", self.r.hgetall(f'{self.name}:{ticker}:finished'))


                    else:
                        self.logger.info("Request not made from data: %r", data)
                    pg += 1
                    
# If this report type is finished, break while loop
                    # if self.ticker_finish[ticker][report_type] is True:
                    #     print (f'Done with this {report_type} of ticker {ticker}')
                    #     break


# Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s tickers from '%s'", found, self.redis_key)

# Close spider if none in queue and amount crawled == amount dequeued
        if self.r.get(self.crawled_count_key) and self.r.get(self.dequeued_count_key):
            if self.r.llen(self.redis_key) == 0 and self.r.get(self.crawled_count_key) >= self.r.get(self.dequeued_count_key):
                
                
                self.logger.info("After finish")
                self.logger.info(self.r.hgetall(f'{self.name}:{ticker}:finished'))

                keys = self.r.keys(f'{self.name}*')
                for k in keys:
                    self.r.delete(k)

                self.crawler.engine.close_spider(spider=self, reason="Queue is empty, the spider closes")

    def make_request_from_data(self, ticker, report_type, page):
        """Replaces the default method, data is a ticker.
        """

        
        self.logger.info(f'MAKING REQUEST FOR {report_type} OF TICKER {ticker} ON PAGE {page}')


        self.fi["formdata"]["Code"] = ticker
        self.fi["formdata"]["ReportType"] = report_type
        self.fi["formdata"]["Page"] = page
        self.fi["meta"]["ticker"] = ticker
        self.fi["meta"]["ReportType"] = report_type
        self.fi["meta"]["Page"] = page

        return FormRequest(url=self.fi["url"],
                            formdata=self.fi["formdata"],
                            headers=self.fi["headers"],
                            cookies=self.fi["cookies"],
                            meta=self.fi["meta"],
                            callback=self.parse
                            )
    
    def parse(self, response):
        resp_json = json.loads(response.text)
        ticker = response.meta['ticker']
        report_type = response.meta['ReportType']
        page = response.meta['Page']


        self.logger.info(f'PARSING RESPONSE FOR {report_type} OF TICKER {ticker} ON PAGE {page}')


            # if response:
                # resp_json = json.loads(response.text)
                # ticker = response.meta['ticker']
                # report_type = response.meta['ReportType']
                # page = response.meta['Page']

        self.logger.info("inside parse")
        self.logger.info(self.r.hgetall(f'{self.name}:{ticker}:finished'))

    # If the first obj in response is empty, then we've finished the report type
        if resp_json[0] == []:
            self.r.hset(f'{self.name}:{ticker}:finished', report_type, "1")
        else:
            save_jsonfile(resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_Page_{page}.json')
            c = self.r.incr(self.crawled_count_key)
            self.logger.info(f'Crawled {c} ticker-reports-page so far')
