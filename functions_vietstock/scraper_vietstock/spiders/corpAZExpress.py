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
        self.fin_insur_tickers_key = fin_insur_tickers_key
        self.all_tickers_key = all_tickers_key

    def parse_redis_queue(self, tickers_list, page, bizType_title, ind_name, total_records):
        '''
        Add information to Redis queue for other Spiders to crawl and for other purposes
        '''

        # If the tickers list is not empty:
        # - Add the bizType and ind_name to available bizType_ind combinations set
        # - Set biz id and ind id for each ticker, which is a key in Redis
        # - Push tickers into Redis queue for financeInfo and other spiders to consume
        self.r.sadd(bizType_ind_set_key, f'{bizType_title};{ind_name}')
        for t in tickers_list:
            self.r.set(t, f'{bizType_title};{ind_name}')

        if page == 1:
            self.r.incrby(self.all_tickers_key, amount=total_records)
        
        # Count the total number of records for `Finance and Insurance` industry
        # As of 2021-05-18: Only push non-finance industries into queue
        if ind_name == "Finance and Insurance":
            if page == 1:
                self.r.incrby(self.fin_insur_tickers_key, amount=total_records)
        else:
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
        bizType_ind_list = sorted(list(self.r.smembers(bizType_ind_set_key)))
        save_jsonfile(bizType_ind_list, filename='schemaData/bizType_ind_list.json')
        self.r.set(closed_redis_key, "1")
        self.logger.info(f'Closing... Setting closed signal value to {self.r.get(closed_redis_key)}')
        self.logger.info(f'Tickers have been pushed into {str(tickers_redis_keys)}')

        fin_insur_count = self.r.get(self.fin_insur_tickers_key)
        all_count = self.r.get(self.all_tickers_key)
        self.logger.info(f'There are {fin_insur_count} tickers in the Finance and Insurance industry')
        self.logger.info(f'There are {all_count} in all')
