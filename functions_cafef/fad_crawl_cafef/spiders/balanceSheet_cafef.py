# -*- coding: utf-8 -*-

import json
import re

from scrapy import Request
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from fad_crawl_cafef.helpers.processingData import rmvEmpStr, simplifyText
from fad_crawl_cafef.helpers.fileDownloader import save_jsonfile
from fad_crawl_cafef.spiders.fadRedis_cafef import fadRedisCafeFSpider
from fad_crawl_cafef.spiders.models.bs_cafef import *
from fad_crawl_cafef.spiders.models.constants import (BACKWARDS_YEAR,
                                                      CURRENT_YEAR,
                                                      REPORT_TERMS)

### copy the `make requests` method from financeInfo spider
### modify the method to fetch the keys pushed into Redis queue (e.g., "A32;-cong-ty-co-phan-32.chn")
### after fetching, construct an url to the balance sheet report

### use appropriate Scrapy selectors to get data


class balanceSheetCafeFHandler(fadRedisCafeFSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(balanceSheetCafeFHandler, self).__init__(*args, **kwargs)
        self.idling = False

        self.ticker_page_count_key = ticker_page_count_key
        self.r.set(self.ticker_page_count_key, "0")

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
            ticker = params[0]
            long_name = params[1]
            self.idling = False

            ### For each year, construct an URL with the ticker and long name fetched from Redis
            for term in REPORT_TERMS.keys():
                if term == "4":
                    ### If term is quarterly, the step is 1 year
                    for year in range(BACKWARDS_YEAR, CURRENT_YEAR+1):
                        req = self.make_request_from_data(ticker, year, term, long_name)
                        if req:
                            yield req
                            self.r.incr(self.ticker_page_count_key)
                        else:
                            self.logger.info(
                                "Request not made from params: %r", params)
                elif term == "0":
                    ### If term is annually, the step is 4 years,
                    ### because CafeF displays 4 years in one page
                    for year in range(BACKWARDS_YEAR, CURRENT_YEAR+1, 4):
                        req = self.make_request_from_data(ticker, year, term, long_name)
                        if req:
                            yield req
                            self.r.incr(self.ticker_page_count_key)
                        else:
                            self.logger.info(
                                "Request not made from params: %r", params)
            found += 1

        if found:
            self.logger.debug("Read %s params from '%s'",
                              found, self.redis_key)
        self.logger.info(
            f'Total requests supposed to process: {self.r.get(self.ticker_page_count_key)}')

        ### Close spider if corpAZ_cafef is closed and none in queue and spider is idling
        ### Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(self.corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            for k in self.r.keys(f'{self.name}*'):
                self.r.delete(k)
            self.crawler.engine.close_spider(spider=self, 
                reason="CorpAZ is closed; Queue is empty; Processed everything")
            self.close_status()

    def make_request_from_data(self, ticker, year, term, long_name):
        """Replaces the default method, data is a ticker.
        """
        bs_url = bs['url'].format(ticker, year, term, long_name)
        term_name = REPORT_TERMS[term]
        bs['meta']['ticker'] = ticker
        bs['meta']['year'] = year
        bs['meta']['report_term'] = term_name

        return Request(url=bs_url,
                        headers=bs["headers"],
                        cookies=bs["cookies"],
                        meta=bs["meta"],
                        callback=self.parse,
                        errback=self.handle_error)

    def parse(self, response):
        """Just crawl
        """
        if response:
            ticker = response.meta['ticker']
            year = response.meta['year']
            report_term_name = response.meta['report_term']
            report_type = response.meta['report_type']
            result = {'data': []}
            
            try:
                ### Extract period stamps (e.g., Q1 2019, Q2 2019,...)
                periods = response.xpath(
                    "//table[@id='tblGridData']/descendant::td[@class='h_t']/text()").extract()
                periods_spl = [simplifyText(p) for p in periods]
                result['periods'] = periods_spl

                ### Extract finance data
                ### NOTE: In a GUI browser, there's an element <tbody> under the <table>,
                ### but in terminals or Postman it never shows, hence the following XPath
                data_trs = response.xpath("//table[@id='tableContent']/child::tr")
                for tr in data_trs:
                    tr_id = tr.xpath("./@id").extract_first()
                    tds_data = [td.xpath('string()').extract()[0] for td in tr.xpath("./child::td")[:-1]]
                    # print(tds_data)
                    tr_data_spl = [tr_id] + [re.sub('\s+',' ',d).strip() for d in tds_data]
                    # print(tr_data_spl)
                    result['data'].append(tr_data_spl)

                ### Write local data files
                save_jsonfile(result, 
                    filename=f'schemaData/{self.name}/{ticker}_{report_type}_{report_term_name}_{year}.json')

                ### Remove error items and crawl next page
                self.r.srem(self.error_set_key, f'{ticker};{report_type};{report_term_name};{year}')
            except Exception as e:
                self.logger.info(f'Exception: {e}')
                self.r.sadd(self.error_set_key, f'{ticker};{report_type};{report_term_name};{year}')
