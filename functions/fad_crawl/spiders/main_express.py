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
from fad_crawl.spiders.models.constants import REDIS_HOST
from fad_crawl.spiders.models.corporateaz import (bizType_ind_set_key,
                                                  business_type,
                                                  closed_redis_key)
from fad_crawl.spiders.models.corporateaz import data as az
from fad_crawl.spiders.models.corporateaz import (industry_list, name_express,
                                                  name_regular,
                                                  settings_express,
                                                  settings_regular,
                                                  tickers_redis_keys)
from fad_crawl.spiders.pdfDocs import pdfDocsHandler
from fad_crawl.helpers.fileDownloader import save_jsonfile

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
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()

    def start_requests(self):
        """Get business types first
        """
        req = Request(url=business_type["url"],
                      headers=business_type["headers"],
                      cookies=business_type["cookies"],
                      callback=self.parse_biz_type,
                      errback=self.handle_error)
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
                                      errback=self.handle_error)
                    yield req
            except Exception as e:
                self.logger.info("Response cannot be parsed by JSON at parse_ind_list")

    def parse_az(self, response):
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
                ### Only get random `SAMPLE_SIZE` tickers, because it's express!
                if SAMPLE_SIZE <= len(res):
                    rand = random.sample(res, SAMPLE_SIZE)
                else:
                    rand = res

                ### Change back to `rand` later...
                tickers_list = [d['Code'] for d in res]

                self.logger.info(
                    f'Found these tickers on page {page}: {str(tickers_list)}')

                ### Push tickers into financeInfo and other spiders
                ### Add the bizType and ind_name to available bizType_ind combinations set
                ### Set biz id and ind id for each ticker, which is a key in Redis
                if tickers_list != []:
                    self.r.sadd(bizType_ind_set_key, f'{bizType_title};{ind_name}')
                    for t in tickers_list:
                        self.r.set(t, f'{bizType_title};{ind_name}')
                        self.r.lpush(tickers_redis_keys[0], f'{t};1')
                        for k in tickers_redis_keys[1:]:
                            self.r.lpush(k, t)
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
        if os.path.exists(self.statusfilepath):
            os.remove(self.statusfilepath)
            self.logger.info(f'Deleted status file at {self.statusfilepath}')
