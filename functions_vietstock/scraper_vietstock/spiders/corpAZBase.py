# Base Spider for all corpAZ Spiders

import json
import os
import scrapy
from scrapy import FormRequest, Request

import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.spiders.models.corporateaz import *


class corporateazBaseHandler(scrapy.Spider):
    '''
    Base corporateAZ Spider
    '''

    name = name_base

    def __init__(self, *args, **kwargs):
        super(corporateazBaseHandler, self).__init__(*args, **kwargs)
        self.statusfilepath = f'run/scrapy/{self.name}.scrapy'
        os.makedirs(os.path.dirname(self.statusfilepath), exist_ok=True)
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()

    def start_requests(self):
        '''
        A request for business types
        '''
        req = Request(url=business_type["url"],
                      headers=business_type["headers"],
                      cookies=business_type["cookies"],
                      callback=self.parse_biz_type,
                      errback=self.handle_error,
                      dont_filter=True)
        yield req

    def parse_biz_type(self, response):
        '''
        After getting a business type, make a request for industries
        '''

        if response:
            try:
                resp_json = json.loads(response.text)
                for bt in resp_json:
                    industry_list["meta"]["bizType_id"] = str(bt["ID"])
                    industry_list["meta"]["bizType_title"] = bt["Title"]
                    req = Request(url=industry_list["url"],
                                  headers=industry_list["headers"],
                                  cookies=industry_list["cookies"],
                                  meta=industry_list["meta"],
                                  callback=self.parse_ind_list,
                                  errback=self.handle_error,
                                  dont_filter=True)
                    yield req
            except Exception as exc:
                self.logger.info(f'Response cannot be parsed by JSON at parse_biz_type: {exc}')

    def parse_ind_list(self, response):
        '''
        After having info on business types and industries, make
        requests for corporateAZ to get tickers of each pair type-industry
        '''

        if response:
            try:
                resp_json = json.loads(response.text)
                bizType_id = response.meta['bizType_id']
                bizType_title = response.meta['bizType_title']
                for ind in resp_json:
                    data["meta"]["bizType_id"] = bizType_id
                    data["meta"]["bizType_title"] = bizType_title
                    data["meta"]["ind_id"] = str(ind["ID"])
                    data["meta"]["ind_name"] = ind["Name"]
                    data["formdata"]["businessTypeID"] = bizType_id
                    data["formdata"]["industryID"] = str(ind["ID"])
                    data["formdata"]["orderBy"] = "TotalShare"
                    data["formdata"]["orderDir"] = "DESC"
                    req = FormRequest(url=data["url"],
                                      formdata=data["formdata"],
                                      headers=data["headers"],
                                      cookies=data["cookies"],
                                      meta=data["meta"],
                                      callback=self.parse_az,
                                      errback=self.handle_error,
                                      dont_filter=True
                    )
                    yield req
            except Exception as exc:
                self.logger.info(f'Response cannot be parsed by JSON at parse_ind_list: {exc}')

    def parse_az(self, response):
        '''
        Process the list of tickers by sending them into Redis queue
        for financeInfo Spider to consume
        '''

        if response:
            page = int(response.meta['page'])
            total_pages = response.meta['TotalPages']
            bizType_id = response.meta['bizType_id']
            bizType_title = response.meta['bizType_title']
            ind_id = response.meta['ind_id']
            ind_name = response.meta['ind_name']
            try:
                resp_json = json.loads(response.text)
                tickers_list = [d['Code'] for d in resp_json]
                self.logger.info(f'Found these tickers on page {page} of {bizType_title};{ind_name}: {tickers_list}')

                if tickers_list != []:
                    # Total pages need to be calculated (for 1st page) or 
                    # delivered from meta of previous page's request
                    total_records = resp_json[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages
                    )
                    self.logger.info(f'Found {total_records} ticker(s) for {bizType_title};{ind_name}')
                    self.logger.info(f'That equals to {total_pages} page(s) for {bizType_title};{ind_name}')

                    # For AZExpress: Push info into Redis queues if the function is defined
                    if getattr(self, "parse_redis_queue", None):
                        getattr(self, "parse_redis_queue")(tickers_list, page, bizType_title, ind_name, total_records)

                    # For AZOnDemand: Aggregate bizType, industry, and ticker data if the function is defined
                    if getattr(self, "parse_biztype_indu_tickers", None):
                        getattr(self, "parse_biztype_indu_tickers")(tickers_list, bizType_title, ind_name)

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

    def closed(self, reason="Spider Finished"):
        '''
        This function will be called when this Spider closes
        '''
        
        # For AZExpress: Some closing procedures on Redis queue if the function is defined
        if getattr(self, "closed_redis_queue", None):
            getattr(self, "closed_redis_queue")()

        # For AZOnDemand: Save result procedure
        if getattr(self, "save_OnDemand_result", None):
            getattr(self, "save_OnDemand_result")()
        
        self.close_status()

    def close_status(self):
        '''
        Clear running status file as part of closing procedure
        '''
        
        if os.path.exists(self.statusfilepath):
            os.remove(self.statusfilepath)
            self.logger.info(f'Deleted status file at {self.statusfilepath}')
    
    def handle_error(self, failure):
        '''
        I don't know why this is here...
        '''

        self.logger.info(str(failure.type))
        self.logger.info(str(failure.getErrorMessage()))
