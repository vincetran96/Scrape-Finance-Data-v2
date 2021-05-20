# Base Spider for all corpAZ Spiders

import scrapy

from scraper_vietstock.spiders.models.corporateaz import *


class corporateazBaseHandler(scrapy.Spider):
    '''
    Base corporateAZ Spider
    '''

    name = name_base

    def __init__(self, *args, **kwargs):
        super(corporateazBaseHandler, self).__init__(*args, **kwargs)

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