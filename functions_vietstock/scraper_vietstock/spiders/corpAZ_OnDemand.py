# This Spider gets corpAZ info on demand of the user
# Syntax:
# scrapy crawl corporateAZOnDemand

import os
import json
import scrapy
from scrapy import FormRequest, Request

import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.spiders.models.corporateaz import *
from scraper_vietstock.helpers.fileDownloader import save_jsonfile


class corporateazOnDemand(scrapy.Spider):
    '''
    CorporateAZ Spider for getting corpAZ info on demand, without using Redis queue
    Instead, at the end, it exports a dict of biztype;indu and tickers within each pair
    '''

    name = name_ondemand

    def __init__(self, *args, **kwargs):
        super(corporateazOnDemand, self).__init__(*args, **kwargs)
        self.statusfilepath = f'run/scrapy/{self.name}.scrapy'
        os.makedirs(os.path.dirname(self.statusfilepath), exist_ok=True)
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()
        self.bizType_indu_tickers = {}

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

                # If the tickers list is not empty:
                # - Add the bizType and ind_name to available bizType_ind combinations set
                # - Set biz id and ind id for each ticker, which is a key in Redis
                # - Push tickers into Redis queue for financeInfo and other spiders to consume
                if tickers_list != []:
                    key =  f'{bizType_title};{ind_name}'
                    if key not in self.bizType_indu_tickers:
                        self.bizType_indu_tickers[key] = tickers_list
                    else:
                        self.bizType_indu_tickers[key] += tickers_list

                    # Total pages need to be calculated (for 1st page) or 
                    # delivered from meta of previous page's request
                    total_records = resp_json[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages
                    )
                    self.logger.info(f'Found {total_records} ticker(s) for {bizType_title};{ind_name}')
                    self.logger.info(f'That equals to {total_pages} page(s) for {bizType_title};{ind_name}')

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
                self.logger.info(f'Response cannot be parsed by JSON at parse_az: {exec}')
        else:
            self.logger.info("Response is null")

    def closed(self, reason="CorporateAZOnDemand Finished"):
        '''
        This function will be called when this Spider closes
        '''

        # Write bizType_indu_tickers dict to a file
        save_jsonfile(self.bizType_indu_tickers, filename='schemaData/bizType_ind_list.json')
        
        # Closing procedures
        self.close_status()

    def handle_error(self, failure):
        '''
        I don't know why this is here...
        '''

        self.logger.info(str(failure.type))
        self.logger.info(str(failure.getErrorMessage()))

    def close_status(self):
        '''
        Clear running status file as part of closing procedure
        '''
        
        if os.path.exists(self.statusfilepath):
            os.remove(self.statusfilepath)
            self.logger.info(f'Deleted status file at {self.statusfilepath}')
