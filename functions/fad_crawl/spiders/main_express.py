# -*- coding: utf-8 -*-
# This spider crawls the list of company names (tickers) on Vietstock,
# feeds the list to the Redis server for other Spiders to crawl

import json
import logging
import os
import random
import sys
import traceback

import redis
import scrapy
from scrapy import FormRequest, Request
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy_redis.spiders import RedisSpider
from twisted.internet import reactor

import fad_crawl.spiders.models.constants as constants
import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.models.constants import REDIS_HOST
from fad_crawl.spiders.models.corporateaz import (all_tickers_key,
                                                  bizType_ind_set_key,
                                                  business_type,
                                                  closed_redis_key)
from fad_crawl.spiders.models.corporateaz import data as az
from fad_crawl.spiders.models.corporateaz import (fin_insur_tickers_key,
                                                  industry_list, name_express,
                                                  name_regular,
                                                  settings_express,
                                                  settings_regular,
                                                  tickers_redis_keys)
from fad_crawl.spiders.pdfDocs import pdfDocsHandler

TEST_TICKERS_LIST = ["AAA", "A32", "VIC"]
TEST_NUM_PAGES = 2
SAMPLE_SIZE = 5


class corporateazExpressHandler(scrapy.Spider):
    """Express CorporateAZ for crawling tickers with specific business types
    and industries
    """
    name = name_express
    custom_settings = settings_express

    def __init__(self, tickers_list="", *args, **kwargs):
        super(corporateazExpressHandler, self).__init__(*args, **kwargs)
        self.r = redis.Redis(host=REDIS_HOST, decode_responses=True)
        self.r.set(closed_redis_key, "0")
        self.statusfilepath = f'run/scrapy/{self.name}.scrapy'
        os.makedirs(os.path.dirname(self.statusfilepath), exist_ok=True)
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()
        self.fin_insur_tickers_key = fin_insur_tickers_key
        self.all_tickers_key = all_tickers_key

    def start_requests(self):
        """Get business types first
        """
        req = Request(url=business_type["url"],
                      headers=business_type["headers"],
                      cookies=business_type["cookies"],
                      callback=self.parse_biz_type,
                      errback=self.handle_error,
                      dont_filter=True)
        yield req

    def parse_biz_type(self, response):
        """Then get industry list
        """
        if response:
            try:
                res = json.loads(response.text)

                for bt in res:
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
            except:
                self.logger.info("Response cannot be parsed by JSON at parse_biz_type")

    def parse_ind_list(self, response):
        """Push all biz types and industries into meta for corpAZ requests
        """

        if response:
            try:
                res = json.loads(response.text)
                bizType_id = response.meta['bizType_id']
                bizType_title = response.meta['bizType_title']

                for ind in res:
                    az["meta"]["bizType_id"] = bizType_id
                    az["meta"]["bizType_title"] = bizType_title
                    az["meta"]["ind_id"] = str(ind["ID"])
                    az["meta"]["ind_name"] = ind["Name"]
                    az["formdata"]["businessTypeID"] = bizType_id
                    az["formdata"]["industryID"] = str(ind["ID"])
                    az["formdata"]["orderBy"] = "TotalShare"
                    az["formdata"]["orderDir"] = "DESC"
                    req = FormRequest(url=az["url"],
                                      formdata=az["formdata"],
                                      headers=az["headers"],
                                      cookies=az["cookies"],
                                      meta=az["meta"],
                                      callback=self.parse_az,
                                      errback=self.handle_error,
                                      dont_filter=True)
                    yield req
            except Exception as e:
                self.logger.info("Response cannot be parsed by JSON at parse_ind_list")

    def parse_az(self, response):
        """In this 'express' version of corpAZ, we only crawl the first page
        """
        if response:
            page = int(response.meta['page'])
            total_pages = response.meta['TotalPages']
            bizType_id = response.meta['bizType_id']
            bizType_title = response.meta['bizType_title']
            ind_id = response.meta['ind_id']
            ind_name = response.meta['ind_name']

            self.logger.info(bizType_title)
            self.logger.info(ind_name)

            try:
                res = json.loads(response.text)
                ### Only get random `SAMPLE_SIZE` tickers, because it's express
                if SAMPLE_SIZE <= len(res):
                    rand = random.sample(res, SAMPLE_SIZE)
                else:
                    rand = res

                ### Change back to `rand` later...
                ### Right now getting all tickers on the page
                tickers_list = [d['Code'] for d in res]

                self.logger.info(
                    f'Found these tickers on page {page}: {str(tickers_list)}')

                ### If the tickers list is not empty:
                ### Add the bizType and ind_name to available bizType_ind combinations set
                ### Set biz id and ind id for each ticker, which is a key in Redis
                ### Push tickers into financeInfo and other spiders
                if tickers_list != []:
                    self.r.sadd(bizType_ind_set_key, f'{bizType_title};{ind_name}')
                    for t in tickers_list:
                        self.r.set(t, f'{bizType_title};{ind_name}')

                    ### Total pages need to be calculated or delivered from previous request's meta
                    total_records = res[0]['TotalRecord']
                    total_pages =  total_records // int(
                        constants.PAGE_SIZE) + 1 if total_pages == "" else int(total_pages)
                    self.logger.info(f'Found {total_pages} page(s) for {bizType_title};{ind_name}')
                    self.logger.info(f'That equals to {total_records} ticker(s) for {bizType_title};{ind_name}')
                    
                    ### Count the total number of records for `Finance and Insurance` industry
                    ### August 11, 2020: Only push non-finance industries
                    if ind_name == "Finance and Insurance":
                        if page == 1:
                            self.r.incrby(self.fin_insur_tickers_key, amount=total_records)
                    else:
                        for t in tickers_list:
                            self.r.lpush(tickers_redis_keys[0], f'{t};1')
                            for k in tickers_redis_keys[1:]:
                                self.r.lpush(k, t)

                    ### Count the total number of records
                    if page == 1:
                        self.r.incrby(self.all_tickers_key, amount=total_records)

                    ### If current page < total pages, send next request
                    if page < total_pages:
                        next_page = str(page + 1)
                        self.logger.info(f'Crawling page {next_page} of total {total_pages} for {bizType_title};{ind_name}')
                        az["meta"]["page"] = next_page
                        az["meta"]["TotalPages"] = str(total_pages)
                        az["meta"]["bizType_id"] = bizType_id
                        az["meta"]["bizType_title"] = bizType_title
                        az["meta"]["ind_id"] = ind_id
                        az["meta"]["ind_name"] = ind_name
                        az["formdata"]["page"] = next_page
                        az["formdata"]["businessTypeID"] = bizType_id
                        az["formdata"]["industryID"] = ind_id
                        az["formdata"]["orderBy"] = "TotalShare"
                        az["formdata"]["orderDir"] = "DESC"
                        req_next = FormRequest(url=az["url"],
                                      formdata=az["formdata"],
                                      headers=az["headers"],
                                      cookies=az["cookies"],
                                      meta=az["meta"],
                                      callback=self.parse_az,
                                      errback=self.handle_error,
                                      dont_filter=True)
                        yield req_next
            except:
                self.logger.info("Response cannot be parsed by JSON at parse_az")
        else:
            self.logger.info("Response is null")

    def closed(self, reason="CorporateAZ-Express Finished"):
        ### Write bizType and ind set to a file for mapping work later
        bizType_ind_list = sorted(list(self.r.smembers(bizType_ind_set_key)))
        save_jsonfile(bizType_ind_list, filename='schema/bizType_ind_list.json')
        
        ### Closing procedures
        self.r.set(closed_redis_key, "1")
        self.close_status()
        self.logger.info(
            f'Closing... Setting closed signal value to {self.r.get(closed_redis_key)}')
        self.logger.info(
            f'Tickers have been pushed into {str(tickers_redis_keys)}')

    def handle_error(self, failure):
        self.logger.info(str(failure.type))
        self.logger.info(str(failure.getErrorMessage()))

    def close_status(self):
        """Clear running status file after closing
        """
        fin_insur_count = self.r.get(self.fin_insur_tickers_key)
        all_count = self.r.get(self.all_tickers_key)
        self.logger.info(f'There are {fin_insur_count} tickers in the Finance and Insurance industry')
        self.logger.info(f'There are {all_count} in all')
        
        if os.path.exists(self.statusfilepath):
            os.remove(self.statusfilepath)
            self.logger.info(f'Deleted status file at {self.statusfilepath}')
