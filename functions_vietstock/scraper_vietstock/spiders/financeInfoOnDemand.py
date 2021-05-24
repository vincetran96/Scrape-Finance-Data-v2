# This Spider scrapes finance info on demand (i.e., for a specific ticker)

import json
from scrapy import FormRequest
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from scraper_vietstock.helpers.fileDownloader import save_jsonfile
from scraper_vietstock.spiders.models.financeinfo import *
from scraper_vietstock.spiders.scraperVSRedis import scraperVSRedisSpider


class financeInfoOnDemandHandler(scraperVSRedisSpider):
    '''
    On demand financeInfo spider
    Command line syntax: scrapy crawl financeInfoOnDemand -a ticker=AAA,BBB -a report_type=CDKT,KQKD -a report_term=2
    '''

    name = name_ondemand
    custom_settings = settings_ondemand

    def __init__(self, *args, **kwargs):
        super(financeInfoOnDemandHandler, self).__init__(*args, **kwargs)
        self.idling = False
        self.r.flushdb()

    def start_requests(self):
        '''
        Replaces the default method.
        '''

        if getattr(self, "page", None):
            page = self.page
        else:
            page = "1"
        for ticker in self.ticker.split(","):
            for report_type in self.report_type.split(","):
                for report_term in self.report_term.split(","):
                    self.r.lpush(
                        self.redis_key, f'{ticker};{page};{report_type};{report_term}'
                    )
        return self.next_requests()
    
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
            report_type = params[2]
            report_term = params[3]
            self.idling = False
            req = self.make_request_from_data(ticker, report_type, page, report_term)
            if req:
                yield req
                self.logger.info(f'Begin scraping page {page} of report {report_type} - term {report_term} - ticker {ticker}')
            else:
                self.logger.info("Request not made from params: %r", params)
        
        # Close Spider if queue is empty and Spider is idling
        if self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="Queue is empty; Spider is idling"
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
        Parse response
        '''

        if response:
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['page']
            report_term = response.meta['ReportTermType']
            self.logger.info(f'On page {page} of {report_type} for {ticker}')
            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                if resp_json[0] == []:
                    self.logger.info(f'DONE ALL PAGES OF {report_type} FOR TICKER {ticker}')
                else:                    
                    save_jsonfile(
                        resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json'
                    )
                    # Remove any errors in the error set and crawl next page
                    self.r.srem(self.error_set_key, f'{ticker};{page};{report_type};{report_term}')
                    next_page = str(int(page) + 1)
                    self.r.lpush(self.redis_key, f'{ticker};{next_page};{report_type};{report_term}')
            except Exception as e:
                self.logger.info(f'Exception at {page} of {report_type} for {ticker}: {e}')
                self.r.sadd(self.error_set_key, f'{ticker};{page};{report_type};{report_term}')