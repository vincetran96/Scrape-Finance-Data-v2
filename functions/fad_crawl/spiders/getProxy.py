# -*- coding: utf-8 -*-
# This spider crawls a list of usable proxies and feed into a Redis key for other spiders to use
# This spider may need to run every 5 minutes during the crawling session (as per ProxyScrape)

import redis
import scrapy
from scrapy import Request

from fad_crawl.spiders.models.constants import PROXIES_REDIS_KEY

PROXY_LIST_FREEPROXY = "https://free-proxy-list.net/"
PROXY_LIST_PROXYSCRAPE   = "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=300&country=all&ssl=all&anonymity=all"
PROXY_CHECKER_URL = "https://httpbin.org/ip"


class getProxyHanlder(scrapy.Spider):
    name = "proxyHandler"

    def __init__(self, tickers_list="", *args, **kwargs):
        super(getProxyHanlder, self).__init__(*args, **kwargs)
        self.r = redis.Redis()
        self.raw_proxies_list = []
        self.redisKey = PROXIES_REDIS_KEY

    def start_requests(self):
        '''
        Delete proxies in the key 'acceptedProxies' first
        '''
        self.r.delete(self.redisKey)
        
        req_freeproxy = Request(PROXY_LIST_FREEPROXY, callback=self.parse_freeproxy)
        yield req_freeproxy

        req_proxyscrape = Request(PROXY_LIST_PROXYSCRAPE, callback=self.parse_proxyscrape)
        yield req_proxyscrape

    def parse_freeproxy(self, response):
        for row in response.xpath("//table[@id='proxylisttable']//tbody//tr"):
            tds = row.xpath('./td//text()').extract()
            if tds[-2] == "yes":
                proxy = f'http://{tds[0]}:{tds[1]}'
                self.logger.info(f'GOT THIS PROXY FROM free-proxy: {proxy}')
                req_prx = Request(PROXY_CHECKER_URL,
                                meta={'proxy': proxy},
                                callback=self.parse_proxy)
                yield req_prx

    def parse_proxyscrape(self, response):
        for row in response.text.split():
            proxy = f'http://{row}'
            self.logger.info(f'GOT THIS PROXY FROM ProxyScrape: {proxy}')
            req_prx = Request(PROXY_CHECKER_URL,
                                meta={'proxy': proxy},
                                callback=self.parse_proxy)
            yield req_prx

    def parse_proxy(self, response):
        proxy = response.meta['proxy']
        print (f'Proxy is {proxy}')
        try:
            if response.status == 200:
                proxy = response.meta['proxy']
                self.logger.info(f'ACCEPTED PROXY: {proxy}')
                self.r.lpush(self.redisKey, proxy)
        except:
            pass
