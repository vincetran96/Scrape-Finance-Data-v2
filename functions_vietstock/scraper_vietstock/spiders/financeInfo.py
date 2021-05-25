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

        self.ticker_report_page_count_key = ticker_report_page_count_key
        self.r.set(self.ticker_report_page_count_key, "0")

    def next_requests(self):
        '''
        Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from scraperVSRedis Spider because it has the Page param. in formdata
        '''

        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            params = bytes_to_str(data, self.redis_encoding).split(";")
            ticker = params[0]
            page = params[1]
            self.idling = False

            # If report type is pushed in (as params[2]), this must be a subsequent request from self.parse()
            # Else, loop thru all report types and make requests
            try:
                report_type = params[2]
                for report_term in report_terms.keys():
                    req = self.make_request_from_data(ticker, report_type, page, report_term)
                    if req:
                        yield req
                        self.r.incr(self.ticker_report_page_count_key)
                    else:
                        self.logger.info("Request not made from params: %r", params)
            except:
                for report_type in report_types:
                    for report_term in report_terms.keys():
                        req = self.make_request_from_data(ticker, report_type, page, report_term)
                        if req:
                            yield req
                            self.r.incr(self.ticker_report_page_count_key)
                        else:
                            self.logger.info("Request not made from params: %r", params)
            found += 1
        if found:
            self.logger.debug(f'Read {found} param(s) from {self.redis_key}')
        
        self.logger.info(
            f'Total requests supposed to process: {self.r.get(self.ticker_report_page_count_key)}'
        )

        # Close spider if corpAZ is closed and Spider Redis queue is empty and Spider is idling:
        # - Print requests with errors, then delete all keys related to this Spider
        if self.r.get(self.corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Spider is idling"
            )
            self.close_status()

    def make_request_from_data(self, ticker, report_type, page, report_term):
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

        return FormRequest(url=data["url"],
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
            page = response.meta['page']
            report_term = response.meta['ReportTermType']

            self.logger.info(f'On page {page} of {report_type} for {ticker}')

            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                bizType_title, ind_name = self.r.get(ticker).split(";")

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
                    self.r.lpush(self.redis_key, f'{ticker};{next_page};{report_type}')
            except Exception as e:
                self.logger.info(f'Exception at {page} of {report_type} for {ticker}: {e}')
                self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type}')
