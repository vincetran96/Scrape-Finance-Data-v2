# This Spider scrapes finance info on demand (i.e., for a specific ticker)

import json
from scrapy import FormRequest
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from scraper_vietstock.helpers.fileDownloader import save_jsonfile
import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.spiders.models.financeinfo import *
from scraper_vietstock.spiders.models.corporateaz import data as corpazdata
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

    def start_requests(self):
        '''
        Replaces the default method.
        If `business type and industry` params are provided
        Else, if `ticker` param is provided
        '''

        # if getattr(self, "page", None):
        #     page = self.page
        # else:
        #     page = "1"
        for report_type in self.report_type.split(","):
            for report_term in self.report_term.split(","):
                if getattr(self, "biz_ind_ids", None):
                    bizType_id, ind_id = self.biz_ind_ids.split(";")
                    corpazdata["meta"]["bizType_id"] = bizType_id
                    corpazdata["meta"]["ind_id"] = ind_id
                    corpazdata["meta"]["report_type"] = report_type
                    corpazdata["meta"]["report_term"] = report_term
                    corpazdata["formdata"]["businessTypeID"] = bizType_id
                    corpazdata["formdata"]["industryID"] = ind_id
                    corpazdata["formdata"]["orderBy"] = "TotalShare"
                    corpazdata["formdata"]["orderDir"] = "DESC"
                    req = FormRequest(
                        url=corpazdata['url'],
                        formdata=corpazdata['formdata'],
                        headers=corpazdata['headers'],
                        cookies=corpazdata['cookies'],
                        callback=self.parse_bizType_ind,
                        errback=self.handle_error,
                        dont_filter=True
                    )
                    yield req
                else:
                    for ticker in self.ticker.split(","):
                        self.r.lpush(
                            self.redis_key, f'{ticker};{self.page};{report_type};{report_term}'
                        )
        # else:
        #     for ticker in self.ticker.split(","):
        #         for report_type in self.report_type.split(","):
        #             for report_term in self.report_term.split(","):
        #                 self.r.lpush(
        #                     self.redis_key, f'{ticker};{self.page};{report_type};{report_term}'
        #                 )

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

    def parse_bizType_ind(self, response):
        if response:
            page = int(response.meta['page'])
            total_pages = response.meta['TotalPages']
            bizType_id = response.meta['bizType_id']
            ind_id = response.meta['ind_id']
            report_type = response.meta['report_type']
            report_term = response.meta['report_term']
            try:
                resp_json = json.loads(response.text)
                tickers_list = [d['Code'] for d in resp_json]

                if tickers_list != []:
                    # Total pages need to be calculated (for 1st page) or 
                    # delivered from meta of previous page's request
                    total_records = resp_json[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages
                    )
                    self.logger.info(f'Found {total_records} ticker(s) for {bizType_id};{ind_id}')
                    self.logger.info(f'That equals to {total_pages} page(s) for {bizType_id};{ind_id}')

                    # Push info into Redis queue
                    for ticker in tickers_list:
                        self.r.lpush(
                            self.redis_key, f'{ticker};{self.page};{report_type};{report_term}'
                        )

                    # If current page < total pages, yield a request for the next page
                    if page < total_pages:
                        next_page = str(page + 1)
                        self.logger.info(f'Crawling page {next_page} of total {total_pages} for {bizType_title};{ind_name}')
                        data["meta"]["page"] = next_page
                        data["meta"]["TotalPages"] = str(total_pages)
                        data["meta"]["bizType_id"] = bizType_id
                        data["meta"]["bizType_title"] = bizType_title
                        data["meta"]["ind_id"] = ind_id
                        data["meta"]["ind_name"] = ind_name
                        data["formdata"]["page"] = next_page
                        data["formdata"]["businessTypeID"] = bizType_id
                        data["formdata"]["industryID"] = ind_id
                        data["formdata"]["orderBy"] = "TotalShare"
                        data["formdata"]["orderDir"] = "DESC"
                        req_next = FormRequest(url=data["url"],
                                      formdata=data["formdata"],
                                      headers=data["headers"],
                                      cookies=data["cookies"],
                                      meta=data["meta"],
                                      callback=self.parse_az,
                                      errback=self.handle_error,
                                      dont_filter=True
                        )
                        yield req_next
            except Exception as exc:
                self.logger.info(f'Response cannot be parsed by JSON at parse_az: {exc}')
        else:
            self.logger.info("Response is null")
    
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