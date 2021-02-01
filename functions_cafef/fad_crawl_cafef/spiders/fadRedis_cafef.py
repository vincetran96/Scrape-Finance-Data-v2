# -*- coding: utf-8 -*-
# FAD Redis spider for CafeF - the project's RedisSpiders should be based on this

import json
import logging
import os
import sys

import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DontCloseSpider
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from fad_crawl_cafef.spiders.models.constants import ERROR_SET_SUFFIX, REDIS_HOST
from fad_crawl_cafef.spiders.models.corpaz_cafef import \
    closed_redis_key as corpAZ_closed_key


class fadRedisCafeFSpider(RedisSpider):
    """Base RedisSpider for other spiders in this project
    """
    def __init__(self, *args, **kwargs):
        super(fadRedisCafeFSpider, self).__init__(*args, **kwargs)
        self.r = redis.Redis(host=REDIS_HOST, decode_responses=True)
        self.report_types = []
        self.fi = {}

        self.error_set_key = f'{self.name}:{ERROR_SET_SUFFIX}'
        self.corpAZ_closed_key = corpAZ_closed_key
        self.statusfilepath = f'run/scrapy/{self.name}.scrapy'
        
        os.makedirs(os.path.dirname(self.statusfilepath), exist_ok=True)
        with open(self.statusfilepath, 'w') as statusfile:
            statusfile.write('running')
            statusfile.close()

    def spider_idle(self):
        """Overwrites default method
        """
        self.idling = True
        self.logger.info("=== IDLING... ===")
        self.schedule_next_requests()
        raise DontCloseSpider

    def handle_error(self, failure):
        """If there's an error with a request/response, add it to the error set
        """
        if failure.request:
            request = failure.request
            ticker = request.meta['ticker']
            year = request.meta['year']
            report_term = request.meta['report_term']
            report_type = request.meta['report_type']
            
            ### Log and save error information
            self.logger.info(
                f'=== ERRBACK: on request for ticker {ticker}, report {report_type}, term {report_term}, year {year}')
            self.r.sadd(self.error_set_key, f'{ticker};{report_type};{report_term};{year}')
            with open(f'logs/{self.name}_{report_type}_spidererrors_short.log', 'a+') as openfile:
                openfile.write("ticker: {0}, report: {1}, term: {2}, year: {3} error type: {4} \n".format(
                    ticker, report_type, report_term, year, str(failure.type)))
        
        elif failure.value.response:
            response = failure.value.response
            ticker = response.meta['ticker']
            year = request.meta['year']
            report_term = request.meta['report_term']
            report_type = request.meta['report_type']

            ### Log and save error information
            self.logger.info(
                f'=== ERRBACK: on request for ticker {ticker}, report {report_type}, term {report_term}, year {year}')
            self.r.sadd(self.error_set_key, f'{ticker};{report_type};{report_term};{year}')
            with open(f'logs/{self.name}_{report_type}_spidererrors_short.log', 'a+') as openfile:
                openfile.write("ticker: {0}, report: {1}, term: {2}, year: {3} error type: {4} \n".format(
                    ticker, report_type, report_term, year, str(failure.type)))

    def close_status(self):
        """Clear running status file after closing
        """
        if os.path.exists(self.statusfilepath):
            os.remove(self.statusfilepath)
            self.logger.info(f'Deleted status file at {self.statusfilepath}')
