# This spider crawls the list of company names (tickers) on Vietstock,
# feeds the list to the Redis queue for other Spiders to crawl

import json
import os
import redis
import scrapy
from scrapy import FormRequest, Request

import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.helpers.fileDownloader import save_jsonfile
from scraper_vietstock.spiders.models.constants import REDIS_HOST
from scraper_vietstock.spiders.models.corporateaz import *
from scraper_vietstock.spiders.corpAZBase import corporateazBaseHandler


class corporateazExpressHandler(corporateazBaseHandler):
    '''
    Express CorporateAZ for crawling tickers with specific business types
    and industries
    '''
    
    name = name_express
    custom_settings = settings_express

    def __init__(self, *args, **kwargs):
        super(corporateazExpressHandler, self).__init__(*args, **kwargs)
        
        # Redis-specific attributes
        self.r = redis.Redis(host=REDIS_HOST, decode_responses=True)
        self.r.set(closed_redis_key, "0")
        self.all_tickers_key = all_tickers_key

    def push_corpAZtickers_queue(self, tickers_list, page, total_records):
        '''
        Add information to Redis queue for other Spiders to crawl and for other purposes
        '''

        # If the tickers list is not empty, push tickers into Redis queue for
        # financeInfo and other spiders to consume
        if page == 1:
            self.r.incrby(self.all_tickers_key, amount=total_records)
        for t in tickers_list:
            # Push to financeInfo queue needs to be different
            self.r.lpush(tickers_redis_keys[0], f'{t};1')
            # Push to other queues
            for k in tickers_redis_keys[1:]:
                self.r.lpush(k, t)

    def closed_redis_queue(self):
        '''
        Closing procedure for Redis queue
        '''
        
        # Write bizType and ind set to a file for mapping work later
        self.r.set(closed_redis_key, "1")
        self.logger.info(f'Closing... Setting closed signal value to {self.r.get(closed_redis_key)}')
        self.logger.info(f'Tickers have been pushed into {str(tickers_redis_keys)}')
        self.logger.info(f'There are {self.r.get(self.all_tickers_key)} tickers in all')
