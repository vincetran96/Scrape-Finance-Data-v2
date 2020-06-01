# -*- coding: utf-8 -*-
# This spider crawls a list of usable proxies and feed into a Redis key for other spiders to use

import scrapy
import redis
from scrapy import Request


PROXY_LIST_URL = "https://free-proxy-list.net/"
PROXY_CHECKER_URL = "https://httpbin.org/ip"


class getProxyHanlder(scrapy.Spider):
    name = "proxyHandler"

    def __init__(self, tickers_list="", *args, **kwargs):
        super(getProxyHanlder, self).__init__(*args, **kwargs)
        self.r = redis.Redis()
        self.raw_proxies_list = []
        self.redisKey = "acceptedProxies"

    def start_requests(self):
        '''
        Delete proxies in the key 'acceptedProxies' first
        '''
        self.r.delete(self.redisKey)
        req = Request(PROXY_LIST_URL, callback=self.parse)
        yield req

    def parse(self, response):
        for row in response.xpath("//table[@id='proxylisttable']//tbody//tr"):
            tds = row.xpath('./td//text()').extract()
            if tds[-2] == "yes":
                proxy = f'http://{tds[0]}:{tds[1]}'
                self.logger.info(f'GOT THIS PROXY: {proxy}')
                req_prx = Request(PROXY_CHECKER_URL,
                                meta={'proxy': proxy},
                                callback=self.parse_proxy)
                yield req_prx

    def parse_proxy(self, response):
        try:
            if response.status == 200:
                proxy = response.meta['proxy']
                self.logger.info(f'USED PROXY: {proxy}')
                self.r.lpush(self.redisKey, proxy)
        except:
            pass
