# This spider crawls a stock ticker's finance reports on Vietstock

import json
from scrapy import FormRequest
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from scraper_vietstock.helpers.fileDownloader import save_jsonfile
from scraper_vietstock.spiders.models.financeinfo import *
from scraper_vietstock.spiders.scraperVSRedis import scraperVSRedisSpider


class financeInfoHandler(scraperVSRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(financeInfoHandler, self).__init__(*args, **kwargs)
        self.idling = False

    def start_requests(self):
        '''
        Replaces the default method
        '''

        # If run with corpAZ (mass scrape), push params to scrape_key
        if getattr(self, "ticker", None) \
            and getattr(self, "report_type", None) \
            and getattr(self, "report_term", None):
            self.run_with_corpAZ = False
            for ticker in self.ticker.split(","):
                for report_type in self.report_type.split(","):
                    for report_term in self.report_term.split(","):
                        params = f'{ticker};{self.page};{report_type};{report_term}'
                        # self.r.lpush(
                        #     scrape_key, f'{ticker};{self.page};{report_type};{report_term}'
                        # )
                        self.r.sadd(scrape_key, params)
        else:
            self.run_with_corpAZ = True
        
        return self.next_requests()

    def next_requests(self):
        '''
        Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from scraperVSRedis Spider because it has the Page param. in formdata
        '''

        # use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        # fetch_one = self.server.spop if use_set else self.server.lpop
        
        # Using set for params
        fetch_one = self.server.spop

        # If run with corpAZ, fetch data from Redis corpAZ_key
        if self.run_with_corpAZ:
            found = 0
            while found < self.redis_batch_size:
                data = fetch_one(corpAZ_key)
                if not data:
                    break
                params = bytes_to_str(data, self.redis_encoding).split(";")
                ticker = params[0]
                page = params[1]
                self.idling = False

                # If report type and report term are passed in as Spider args, use them
                if getattr(self, "report_type", None) and getattr(self, "report_term", None):
                    for report_type in self.report_type.split(","):
                        for report_term in self.report_term.split(","):
                            req = self.make_request_from_data(ticker, report_type, report_term, page)
                            if req:
                                yield req
                else:
                    # If report type and report term are pushed in Redis queue (as params[2] and params[3]), this must be a subsequent request from self.parse()
                    # Else, loop thru all report types and make requests
                    try:
                        report_type = params[2]
                        report_term = params[3]
                        req = self.make_request_from_data(ticker, report_type, report_term, page)
                        if req:
                            yield req
                        else:
                            self.logger.info("Request not made from params: %r", params)
                    except:
                        for report_type in report_types:
                            for report_term in report_terms.keys():
                                req = self.make_request_from_data(ticker, report_type, report_term, page)
                                if req:
                                    yield req
                                else:
                                    self.logger.info("Request not made from params: %r", params)
                found += 1
            if found:
                self.logger.debug(f'Read {found} param(s) from {corpAZ_key}')
            
            # Close spider if corpAZ is closed and corpAZ Redis queue is empty and Spider is idling:
            # - Print requests with errors, then delete all keys related to this Spider
            # Changed corpAZ_key to set
            if self.r.get(self.corpAZ_closed_key) == "1" \
                and self.r.scard(corpAZ_key) == 0 \
                and self.idling == True:
                
                self.logger.info(
                    f'corpAZ closed key: {self.r.get(self.corpAZ_closed_key)}'
                )
                self.logger.info(
                    f'corpAZ key {corpAZ_key} contains: {self.r.smembers(corpAZ_key)}'
                )
                
                self.logger.info(self.r.smembers(self.error_set_key))
                keys = self.r.keys(f'{self.name}*')
                for k in keys:
                    self.r.delete(k)
                self.crawler.engine.close_spider(
                    spider=self, reason="CorpAZ is closed; CorpAZ queue is empty; Spider is idling"
                )
                self.close_status()
        
        # If not run with corpAZ, fetch data from scrape_key
        else:
            found = 0
            while found < self.redis_batch_size:
                data = fetch_one(scrape_key)
                if not data:
                    break
                params = bytes_to_str(data, self.redis_encoding).split(";")
                ticker = params[0]
                report_type = params[2]
                report_term = params[3]
                page = params[1]
                self.idling = False

                req = self.make_request_from_data(ticker, report_type, report_term, page)
                if req:
                    yield req
                else:
                    self.logger.info("Request not made from params: %r", params)
                found += 1
            if found:
                self.logger.debug(f'Read {found} param(s) from {corpAZ_key}')
            
            # Close spider if scrape_key Redis queue is empty and Spider is idling:
            # - Print requests with errors, then delete all keys related to this Spider
            if self.r.scard(scrape_key) == 0 and self.idling == True:
                self.logger.info(self.r.smembers(self.error_set_key))
                keys = self.r.keys(f'{self.name}*')
                for k in keys:
                    self.r.delete(k)
                self.crawler.engine.close_spider(
                    spider=self, reason="Queue is empty; Spider is idling"
                )
                self.close_status()

    def make_request_from_data(self, ticker, report_type, report_term, page):
        '''
        Replaces the default method, data is a ticker
        '''
        
        data["formdata"]["Code"] = ticker
        data["formdata"]["ReportType"] = report_type
        data["formdata"]["Page"] = page
        data["formdata"]["ReportTermType"] = report_term
        data["meta"]["ticker"] = ticker
        data["meta"]["ReportType"] = report_type
        data["meta"]["page"] = page
        data["meta"]["ReportTermType"] = report_term

        return FormRequest(
            url=data["url"],
            formdata=data["formdata"],
            headers=data["headers"],
            cookies=data["cookies"],
            meta=data["meta"],
            callback=self.parse,
            errback=self.handle_error,
            dont_filter=True
        )
 
    def parse(self, response):
        '''
        If the first obj in response is empty, then we've finished the report type for this ticker
        If there's actual data in response, save JSON and remove {ticker};{page};{report_type} value
        from error list, then crawl the next page
        '''

        if response:
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            report_term = response.meta['ReportTermType']
            page = response.meta['page']
            url = response.url

            self.logger.info(f'On page {page} of {report_type} for {ticker}')

            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                # bizType_title, ind_name = self.r.get(ticker).split(";")

                if resp_json[0] == []:
                    self.logger.info(f'DONE ALL PAGES OF {report_type} FOR TICKER {ticker}')
                else:
                    # Write local data files in an express way
                    # save_jsonfile(
                    #     resp_json, filename=f'localData/schema/{self.name}/{bizType_title}_{ind_name}_{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json')
                    
                    # Writing local data files in the regular way
                    save_jsonfile(
                        resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json'
                    )

                    # Remove error items (regardless exist or not) and crawl next page
                    self.r.srem(self.error_set_key, f'{ticker};{page};{report_type}')
                    next_page = str(int(page) + 1)

                    # Check if new params have already been enqueued
                    enqueued_params = self.r.smembers(enqueued_key)
                    new_params = f'{ticker};{next_page};{report_type};{report_term}'
                    if new_params in enqueued_params:
                        self.logger.warning(
                            f"{new_params} params are already in enqueued params set")
                    else:
                        self.r.sadd(enqueued_key, new_params)
                        if self.run_with_corpAZ:
                            self.r.sadd(corpAZ_key, new_params)
                        else:
                            self.r.sadd(scrape_key, new_params)
                    
            except Exception as exc:
                self.logger.warning(
                    f'Exception at page {page} of {report_type} for {ticker} at {url}: {exc}')
                self.r.sadd(
                    self.error_set_key, f'{ticker};{page};{report_type}')
                # raise exc # not raise error here
        else:
            self.logger.warning('No response')
