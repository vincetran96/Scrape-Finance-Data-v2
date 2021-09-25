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

    def check_enqueued_params(self, params_str: str):
        '''
        Returns `True` if `params_str` in enqueued params set
        '''
        
        enqueued_params = self.r.smembers(enqueued_key)
        if params_str in enqueued_params:
            self.logger.warning(
                f"{params_str} params are already in enqueued params set")
            return True
        return False
    
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
        # fetch_one = self.server.spop

        # If run with corpAZ (corpAZOverview or corpAZExpress),
        #   fetch data from Redis corpAZ_key
        if self.run_with_corpAZ:
            found = 0
            while found < self.redis_batch_size:
            # while self.r.scard(corpAZ_key) > 0:
                data = self.server.spop(corpAZ_key)
                if not data:
                    break
                params_str = bytes_to_str(data, self.redis_encoding) 
                params = params_str.split(";") # params have at least 2 elements
                ticker = params[0]
                page = params[1]

                self.idling = False # Set idling status

                # If report type and report term are pushed in Redis queue (as params[2] and params[3]), this must be a subsequent request from self.parse()
                # Else:
                #   - If run with report_type and report_term args...
                #   - If not, loop thru all report types and make requests
                if len(params) == 4:
                    report_type = params[2]
                    report_term = params[3]
                    full_params_str = f'{ticker};{page};{report_type};{report_term}'
                    if not self.check_enqueued_params(full_params_str):
                        self.r.sadd(enqueued_key, full_params_str)
                        req = self.make_request_from_data(
                            ticker, report_type, report_term, page)
                        if req:
                            yield req
                else:
                    # Report type and report term are passed in as Spider args, use them
                    if getattr(self, "report_type", None) \
                        and getattr(self, "report_term", None):
                        for report_type in self.report_type.split(","):
                            for report_term in self.report_term.split(","):
                                full_params_str = f'{ticker};{page};{report_type};{report_term}'
                                if not self.check_enqueued_params(full_params_str):
                                    self.r.sadd(enqueued_key, full_params_str)
                                    req = self.make_request_from_data(
                                        ticker, report_type, report_term, page)
                                    if req:
                                        yield req
                    else:
                        for report_type in default_report_types:
                            for report_term in default_report_terms.keys():
                                full_params_str = f'{ticker};{page};{report_type};{report_term}'
                                if not self.check_enqueued_params(full_params_str):
                                    self.r.sadd(enqueued_key, full_params_str)
                                    req = self.make_request_from_data(
                                        ticker, report_type, report_term, page)
                                    if req:
                                        yield req   
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
                self.close_status()
                self.crawler.engine.close_spider(
                    spider=self,
                    reason="CorpAZ is closed; CorpAZ queue is empty; Spider is idling"
                )
        
        # If not run with corpAZ, fetch data from scrape_key
        else:
            found = 0
            while found < self.redis_batch_size:
                data = self.server.spop(scrape_key)
                if not data:
                    break
                params = bytes_to_str(data, self.redis_encoding).split(";")
                ticker = params[0]
                report_type = params[2]
                report_term = params[3]
                page = params[1]
                
                self.idling = False

                if not self.check_enqueued_params(params):
                    self.r.sadd(enqueued_key, params)
                    req = self.make_request_from_data(
                        ticker, report_type, report_term, page)
                    if req:
                        yield req
                found += 1
            if found:
                self.logger.debug(f'Read {found} param(s) from {scrape_key}')
            
            # Close spider if scrape_key Redis queue is empty and Spider is idling:
            # - Print requests with errors, then delete all keys related to this Spider
            if self.r.scard(scrape_key) == 0 and self.idling == True:
                self.logger.info(self.r.smembers(self.error_set_key))
                keys = self.r.keys(f'{self.name}*')
                for k in keys:
                    self.r.delete(k)
                self.close_status()
                self.crawler.engine.close_spider(
                    spider=self,
                    reason="Queue is empty; Spider is idling"
                )

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

            self.logger.info(f'On page {page} of report type {report_type}, report term {report_term} for {ticker}')

            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                # bizType_title, ind_name = self.r.get(ticker).split(";")

                if resp_json[0] == []:
                    self.logger.info(
                        f'DONE ALL PAGES OF REPORT TYPE {report_type}, REPORT TERM {report_term} FOR TICKER {ticker}')
                else:
                    # Write local data files in an express way
                    # save_jsonfile(
                    #     resp_json, filename=f'localData/schema/{self.name}/{bizType_title}_{ind_name}_{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json')
                    
                    # Writing local data files in the regular way
                    save_jsonfile(
                        resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_{default_report_terms[report_term]}_Page_{page}.json'
                    )

                    # Remove error items (regardless exist or not) and crawl next page
                    # self.r.srem(self.error_set_key, f'{ticker};{page};{report_type}')
                    next_page = str(int(page) + 1)

                    # Check if new params have already been enqueued
                    new_params_str = f'{ticker};{next_page};{report_type};{report_term}'
                    # if not self.check_enqueued_params(new_params_str):
                    #     self.r.sadd(enqueued_key, new_params_str)
                    if self.run_with_corpAZ:
                        self.r.sadd(corpAZ_key, new_params_str)
                    else:
                        self.r.sadd(scrape_key, new_params_str)     
            except Exception as exc:
                self.logger.warning(
                    f'Exception at page {page} of {report_type} for {ticker} at {url}: {exc}')
                
                # Add error to error set
                self.r.sadd(
                    self.error_set_key, f'{ticker};{page};{report_type};{report_term}')
                
                # Write error to log file
                with open(
                    f'logs/{self.name}_{report_type}_spidererrors_short.log', 'a+') as openfile:
                    openfile.write(
                        f'ticker: {ticker}, report: {report_type}, page {page}, error type: {type(exc)} \n')
                # raise exc # not raise error here
        # else:
        #     self.logger.warning('No response')
