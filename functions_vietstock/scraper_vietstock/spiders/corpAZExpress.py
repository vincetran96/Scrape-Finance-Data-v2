# This spider crawls the list of company names (tickers) on Vietstock,
# feeds the list to the Redis queue for other Spiders to crawl

import redis

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

    def push_corpAZtickers_queue(self, tickers_list, page, total_records, total_pages, bizType_id, ind_id):
        '''
        Add information to Redis queue for other Spiders to crawl and for other purposes
        '''

        # Push tickers into Redis queue for financeInfo and other spiders to consume
        if page == 1:
            self.r.incrby(tickers_totalcount_key, amount=total_records)
            self.logger.info(
                f'Found {total_records} ticker(s) for business type id {bizType_id} - industry id {ind_id}'
            )
            self.logger.info(
                f'That equals to {total_pages} page(s) for business type id {bizType_id} - industry id {ind_id}'
            )
        for t in tickers_list:
            # Push to financeInfo queue needs to be different
            # self.r.lpush(tickers_redis_keys[0], f'{t};1')
            finInfo_enqueued_params = self.r.smembers(financeInfo_enqueued_key)
            new_params = f'{t};1'
            if new_params in finInfo_enqueued_params:
                self.logger.warning(
                    f"{new_params} params are already in finInfo enqueued params set")
            else:
                self.r.sadd(financeInfo_enqueued_key, new_params)
                self.r.sadd(tickers_redis_keys[0], new_params)

            # Push to other queues
            for k in tickers_redis_keys[1:]:
                self.r.lpush(k, t)

    def closed_redis_queue(self):
        '''
        Closing procedure for Redis queue
        '''
        
        # Write bizType and ind set to a file for mapping work later
        self.r.set(closed_redis_key, "1")
        self.logger.info(
            f'Closing... Setting closed signal value of 1 to {self.r.get(closed_redis_key)}'
        )
        self.logger.info(f'Tickers have been pushed into {str(tickers_redis_keys)}')
        self.logger.info(f'There are {self.r.get(tickers_totalcount_key)} tickers in all')
