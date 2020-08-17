# -*- coding: utf-8 -*-

import json
import re

from scrapy import Request
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from fad_crawl_cafef.helpers.processingData import rmvEmpStr, simplifyText
from fad_crawl_cafef.helpers.fileDownloader import save_jsonfile
from fad_crawl_cafef.spiders.fadRedis_cafef import fadRedisCafeFSpider
from fad_crawl_cafef.spiders.models.industriestickers_cafef import *
from fad_crawl_cafef.spiders.models.constants import (BACKWARDS_YEAR,
                                                      CURRENT_YEAR,
                                                      REPORT_TERMS)


### copy the `make requests` method from financeInfo spider
### modify the method to fetch the keys pushed into Redis queue (e.g., "A32;-cong-ty-co-phan-32.chn")
### after fetching, construct an url to the balance sheet report

### use appropriate Scrapy selectors to get data


class industriesTickersCafeFHandler(fadRedisCafeFSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(industriesTickersCafeFHandler, self).__init__(*args, **kwargs)
        self.r.set(industries_tickers_finished, "0")
        self.idling = False

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        """
        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            params = bytes_to_str(data, self.redis_encoding).split(";")
            industry_id = params[0]
            industry_name = params[1]
            total_records = params[2]
            self.idling = False

            ### Make a request from the parameters
            req = self.make_request_from_data(industry_id, industry_name, total_records)
            if req:
                yield req
            else:
                self.logger.info("Request not made from params: %r", params)
            found += 1

        if found:
            self.logger.debug("Read %s params from '%s'", found, self.redis_key)

        ### Close spider if: the pushing of industries is done and none in queue and spider is idling
        ### Delete all keys related to this Spider
        ### Set the IndustriesTickers_cafef key to "1", meaning it has finished finding tickers-industries
        try:
            industries_done = self.r.get(industries_finished)
        except:
            industries_done = "0"
        if  industries_done == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            for k in self.r.keys(f'{self.name}*'):
                self.r.delete(k)
            self.r.set(industries_tickers_finished, "1")
            
            industries_tickers = self.r.lrange(industries_tickers_queue, 0, -1)
            self.logger.info(industries_tickers)
            
            self.crawler.engine.close_spider(spider=self, reason="Industries pushing done; Queue is empty; Processed everything")
            self.close_status()

    def make_request_from_data(self, ind_id, ind_name, total_records):
        """Replaces the default method
        """
        url = indtickers['url'].format(ind_id, total_records)
        indtickers['meta']['industry_id'] = ind_id
        indtickers['meta']['industry_name'] = ind_name

        return Request(url=url,
                        headers=indtickers["headers"],
                        cookies=indtickers["cookies"],
                        meta=indtickers["meta"],
                        callback=self.parse,
                        errback=self.handle_error,
                        dont_filter=True)

    def parse(self, response):
        """Gets the list of tickers of the corresponding industry and push them to queue
        """
        if response:
            ind_name = response.meta['industry_name']
            try:
                s = response.text
                var_j = json.loads(re.findall(r"var CompanyInfo = (.*?);\s*$",s)[0][1:-1])
                tickers = var_j['CompanyInfos']
                for ticker in tickers:
                    ticker_symbol = ticker['Symbol']
                    self.logger.info(f'Found this ticker: {ticker_symbol}')
                    
                    self.r.lpush(industries_tickers_queue, f'{ticker_symbol};{ind_name}')
                    
                    self.logger.info(f'Pushed {ticker_symbol};{ind_name}')
            except Exception as e:
                self.logger.info(f'Exception: {e}')
            

    def handle_error(self, failure):
        """If there's an error with a request/response, add it to the error set
        """
        if failure.request:
            request = failure.request
            industry_id = request.meta['industry_id']
            industry_name = request.meta['industry_name']
            
            ### Log and save error information
            self.logger.info(f'=== ERRBACK: on request for industry id {industry_id}, name {industry_name}')
        
        elif failure.value.response:
            response = failure.value.response
            industry_id = request.meta['industry_id']
            industry_name = request.meta['industry_name']

            ### Log and save error information
            self.logger.info(f'=== ERRBACK: on request for industry id {industry_id}, name {industry_name}')
        