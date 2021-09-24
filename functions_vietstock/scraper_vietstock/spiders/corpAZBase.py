# Base Spider for all corpAZ Spiders

import json
import os
import scrapy
from scrapy import FormRequest, Request
from scrapy_redis.utils import bytes_to_str
import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.spiders.models.corporateaz import *
from scraper_vietstock.spiders.scraperVSRedis import scraperVSRedisSpider


class corporateazBaseHandler(scraperVSRedisSpider):
    '''
    Base corporateAZ Spider
    '''

    name = name_base
    custom_settings = settings_regular

    def __init__(self, *args, **kwargs):
        super(corporateazBaseHandler, self).__init__(*args, **kwargs)
        self.defaultnullmeta = "NOMETATOVIEW"
        self.statusfilepath = f'run/scrapy/{self.name}.scrapy'
        os.makedirs(os.path.dirname(self.statusfilepath), exist_ok=True)
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()

    def start_requests(self):
        '''
        A request for business types
        '''

        # If biz_ind_ids are passed in as Spider args
        if getattr(self, "biz_ind_ids", None):
            bizType_id, ind_id = getattr(self, "biz_ind_ids").split(";")
            # data["meta"]["bizType_id"] = bizType_id
            # data["meta"]["bizType_title"] = defaultnullmeta
            # data["meta"]["ind_id"] = ind_id
            # data["meta"]["ind_name"] = defaultnullmeta
            # data["formdata"]["businessTypeID"] = bizType_id
            # data["formdata"]["industryID"] = ind_id
            # # data["formdata"]["orderBy"] = "TotalShare"
            # # data["formdata"]["orderDir"] = "DESC"
            # req = FormRequest(
            #     url=data["url"],
            #     formdata=data["formdata"],
            #     headers=data["headers"],
            #     cookies=data["cookies"],
            #     meta=data["meta"],
            #     callback=self.parse_az,
            #     errback=self.handle_error,
            #     dont_filter=True
            # )
            req = self.make_request_from_data(
                bizType_id, defaultnullmeta, ind_id, defaultnullmeta
            )
            if req:
                yield req
        # else:
        #     biz_req = Request(
        #         url=business_type["url"],
        #         headers=business_type["headers"],
        #         cookies=business_type["cookies"],
        #         callback=self.parse_biz_type,
        #         errback=self.handle_error,
        #         dont_filter=True
        #     )
        #     if biz_req:
        #         yield biz_req

        else:
            biz_req = Request(
                url=business_type["url"],
                headers=business_type["headers"],
                cookies=business_type["cookies"],
                callback=self.parse_biz_test,
                errback=self.handle_error,
                dont_filter=True
            )
            if biz_req:
                yield biz_req
            
            ind_req = Request(
                url=industry_list["url"],
                headers=industry_list["headers"],
                cookies=industry_list["cookies"],
                meta=industry_list["meta"],
                callback=self.parse_ind_test,
                errback=self.handle_error,
                dont_filter=True
            )
            if ind_req:
                yield ind_req
    
    def parse_biz_test(self, response):
        if response:
            try:
                resp_json = json.loads(response.text)
                bizType_ids = [str(bt["ID"]) for bt in resp_json]
                bizType_titles = [bt["Title"] for bt in resp_json]
                self.r.lpush(bizType_set_key, *bizType_ids)
                self.r.lpush(bizType_title_set_key, *bizType_titles)
            except Exception as exc:
                self.logger.info(
                    f'Response cannot be parsed by JSON at parse_biz_test: {exc}')

    def parse_ind_test(self, response):
        if response:
            try:
                resp_json = json.loads(response.text)
                ind_ids = [str(ind["ID"]) for ind in resp_json]
                ind_titles = [ind["Name"] for ind in resp_json]
                self.r.lpush(ind_set_key, *ind_ids)
                self.r.lpush(ind_name_set_key, *ind_titles)
            except Exception as exc:
                self.logger.info(
                    f'Response cannot be parsed by JSON at parse_ind_test: {exc}')

    def next_requests(self):
        bizTypes = self.server.lrange(bizType_set_key, 0 , -1)
        bizType_titles = self.server.lrange(bizType_title_set_key, 0 , -1)
        inds = self.server.lrange(ind_set_key, 0, -1)
        ind_names = self.server.lrange(ind_name_set_key, 0, -1)

        if ((not bizTypes) or (not inds)):
            if self.idling:
                self.closed()
            else:
                return # return, wait for next call if not idle

        for ib, bizType in enumerate(bizTypes):
            for ii, ind in enumerate(inds):
                bizType_id = bytes_to_str(bizType, self.redis_encoding)
                bizType_title = bytes_to_str(bizType_titles[ib])
                ind_id = bytes_to_str(ind, self.redis_encoding)
                ind_name = bytes_to_str(ind_names[ii])
                req = self.make_request_from_data(
                    bizType_id, bizType_title, ind_id, ind_name
                )
                if req:
                    yield req
        self.server.delete(
            bizType_set_key, bizType_title_set_key,
            ind_set_key, ind_name_set_key
        )

    def make_request_from_data(
            self, bizType_id, bizType_title, ind_id, ind_name,
            page = "1", total_pages = ""
        ):
        '''
        Overrides default method
        '''
        
        data["meta"]["bizType_id"] = bizType_id
        data["meta"]["bizType_title"] = bizType_title
        data["meta"]["ind_id"] = ind_id
        data["meta"]["ind_name"] = ind_name
        data["meta"]["page"] = page
        data["meta"]["TotalPages"] = str(total_pages)
        data["formdata"]["businessTypeID"] = bizType_id
        data["formdata"]["industryID"] = ind_id
        data["formdata"]["page"] = page

        req = FormRequest(
            url=data["url"],
            formdata=data["formdata"],
            headers=data["headers"],
            cookies=data["cookies"],
            meta=data["meta"],
            callback=self.parse_az_test,
            errback=self.handle_error,
            dont_filter=True
        )
        return req

    def parse_az_test(self, response):
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
                if tickers_list:
                    # self.logger.info(tickers_list)

                    total_records = resp_json[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages
                    )
                    self.logger.info(f'Found {total_records} ticker(s) for business type id {bizType_id} - industry id {ind_id}')
                    self.logger.info(f'That equals to {total_pages} page(s) for business type id {bizType_id} - industry id {ind_id}')

                    # For AZExpress: Push info into Redis queues if the function is defined
                    if getattr(self, "push_corpAZtickers_queue", None):
                        getattr(self, "push_corpAZtickers_queue")(
                            tickers_list, page, total_records, total_pages,
                            bizType_id, bizType_title, ind_id, ind_name
                        )

                    # For AZOverview: Aggregate bizType, industry, and ticker data if the function is defined
                    if getattr(self, "overview_biztype_indu_tickers", None):
                        if bizType_title != defaultnullmeta and ind_name != defaultnullmeta:
                            getattr(self, "overview_biztype_indu_tickers")(
                                tickers_list, bizType_id, bizType_title, ind_id, ind_name
                            )

                    # If current page < total pages, yield a request for the next page
                    if page < total_pages:
                        next_page = str(page + 1)
                        self.logger.info(
                            f'Scraping page {next_page} of total {total_pages} for business type id {bizType_id} - industry id {ind_id}')
                        req_next = self.make_request_from_data(
                            bizType_id, bizType_title, ind_id, ind_name,
                            page=next_page, total_pages=total_pages
                        )
                        if req_next:
                            yield req_next
            except Exception as exc:
                self.logger.info(f'Response cannot be parsed by JSON at parse_az: {exc}')
                raise exc

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
                    req = Request(
                        url=industry_list["url"],
                        headers=industry_list["headers"],
                        cookies=industry_list["cookies"],
                        meta=industry_list["meta"],
                        callback=self.parse_ind_list,
                        errback=self.handle_error,
                        dont_filter=True
                    )
                    if req:
                        yield req
            except Exception as exc:
                self.logger.info(
                    f'Response cannot be parsed by JSON at parse_biz_type: {exc}')

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
                    # data["formdata"]["orderBy"] = "TotalShare"
                    # data["formdata"]["orderDir"] = "DESC"
                    req = FormRequest(
                        url=data["url"],
                        formdata=data["formdata"],
                        headers=data["headers"],
                        cookies=data["cookies"],
                        meta=data["meta"],
                        callback=self.parse_az,
                        errback=self.handle_error,
                        dont_filter=True
                    )
                    if req:
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
                # self.logger.info(
                #     f'Found these tickers on page {page} of business type id {bizType_id} - industry id {ind_id}: {tickers_list}')

                if tickers_list:
                    # Total pages need to be calculated (for 1st page) or 
                    # delivered from meta of previous page's request
                    total_records = resp_json[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages
                    )
                    self.logger.info(f'Found {total_records} ticker(s) for business type id {bizType_id} - industry id {ind_id}')
                    self.logger.info(f'That equals to {total_pages} page(s) for business type id {bizType_id} - industry id {ind_id}')

                    # For AZExpress: Push info into Redis queues if the function is defined
                    if getattr(self, "push_corpAZtickers_queue", None):
                        getattr(self, "push_corpAZtickers_queue")(
                            tickers_list, page, total_records, total_pages,
                            bizType_id, bizType_title, ind_id, ind_name
                        )

                    # For AZOverview: Aggregate bizType, industry, and ticker data if the function is defined
                    if getattr(self, "overview_biztype_indu_tickers", None):
                        if bizType_title != defaultnullmeta and ind_name != defaultnullmeta:
                            getattr(self, "overview_biztype_indu_tickers")(
                                tickers_list, bizType_id, bizType_title, ind_id, ind_name
                            )

                    # If current page < total pages, yield a request for the next page
                    if page < total_pages:
                        next_page = str(page + 1)
                        self.logger.info(
                            f'Scraping page {next_page} of total {total_pages} for business type id {bizType_id} - industry id {ind_id}')
                        data["meta"]["page"] = next_page
                        data["meta"]["TotalPages"] = str(total_pages)
                        data["meta"]["bizType_id"] = bizType_id
                        data["meta"]["bizType_title"] = bizType_title
                        data["meta"]["ind_id"] = ind_id
                        data["meta"]["ind_name"] = ind_name
                        data["formdata"]["page"] = next_page
                        data["formdata"]["businessTypeID"] = bizType_id
                        data["formdata"]["industryID"] = ind_id
                        # data["formdata"]["orderBy"] = "TotalShare"
                        # data["formdata"]["orderDir"] = "DESC"
                        req_next = FormRequest(
                            url=data["url"],
                            formdata=data["formdata"],
                            headers=data["headers"],
                            cookies=data["cookies"],
                            meta=data["meta"],
                            callback=self.parse_az,
                            errback=self.handle_error,
                            dont_filter=True
                        )
                        if req_next:
                            yield req_next
            except Exception as exc:
                self.logger.info(f'Response cannot be parsed by JSON at parse_az: {exc}')
                raise exc
        else:
            self.logger.info("Response is null")

    def closed(self, reason="Spider finished"):
        '''
        This function will be called when this Spider closes
        '''
        
        # For AZExpress: Some closing procedures on Redis queue if the function is defined
        if getattr(self, "closed_redis_queue", None):
            getattr(self, "closed_redis_queue")()

        self.close_status()
        self.crawler.engine.close_spider(spider=self, reason=reason)
    
    def handle_error(self, failure):
        '''
        I don't know why this is here...
        '''

        self.logger.info(str(failure.type))
        self.logger.info(str(failure.getErrorMessage()))
