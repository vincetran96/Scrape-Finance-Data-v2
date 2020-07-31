# -*- coding: utf-8 -*-

from scrapy import Request
from scrapy_redis import defaults
from scrapy_redis.utils import bytes_to_str

from fad_crawl_cafef.spiders.fadRedis_cafef import fadRedisCafeFSpider
from fad_crawl_cafef.spiders.models.bs_cafef import *
from fad_crawl_cafef.spiders.models.constants import (BACKWARDS_YEAR,
                                                      CURRENT_YEAR,
                                                      REPORT_TERMS)

### copy the `make requests` method from financeInfo spider
### modify the method to fetch the keys pushed into Redis queue (e.g., "A32;-cong-ty-co-phan-32.chn")
### after fetching, construct an url to the balance sheet report

### use appropriate Scrapy selectors to get data


class balanceSheetCafeFHandler(fadRedisCafeFSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(balanceSheetCafeFHandler, self).__init__(*args, **kwargs)
        self.idling = False

        self.ticker_page_count_key = ticker_page_count_key
        self.r.set(self.ticker_page_count_key, "0")

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        """

        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            params = bytes_to_str(data, self.redis_encoding).split(";")
            ticker = params[0]
            long_name = params[1]
            self.idling = False

            ### For each year, construct an URL with the ticker and long name fetched from Redis
            for year in range(BACKWARDS_YEAR, CURRENT_YEAR+1):
                for term in REPORT_TERMS.keys():
                    req = self.make_request_from_data(ticker, year, term, long_name)
                    if req:
                        yield req
                        self.r.incr(self.ticker_page_count_key)
                    else:
                        self.logger.info(
                            "Request not made from params: %r", params)
            found += 1

        if found:
            self.logger.debug("Read %s params from '%s'",
                              found, self.redis_key)
        self.logger.info(
            f'Total requests supposed to process: {self.r.get(self.ticker_page_count_key)}')

        # Close spider if corpAZ is closed and none in queue and spider is idling
        # Print off requests with errors, then delete all keys related to this Spider
        if self.r.get(self.corpAZ_closed_key) == "1" and self.r.llen(self.redis_key) == 0 and self.idling == True:
            self.logger.info(self.r.smembers(self.error_set_key))
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed; Queue is empty; Processed everything")
            self.close_status()

    def make_request_from_data(self, ticker, year, term, long_name):
        """Replaces the default method, data is a ticker.
        """
        
        bs_url = bs['url'].format(ticker, year, term, long_name)
        term_name = REPORT_TERMS[term]
        return Request(url=bs_url,
                        headers=bs["headers"],
                        cookies=bs["cookies"],
                        meta=bs["meta"],
                        callback=self.parse,
                        errback=self.handle_error)

    def parse(self, response):
        """If the first obj in response is empty, then we've finished the report type for this ticker
        If there's actual data in response, save JSON and remove {ticker};{page};{report_type} value
        from error list, then crawl the next page
        """
        if response:
            ticker = response.meta['ticker']
            report_type = response.meta['ReportType']
            page = response.meta['page']
            report_term = response.meta['ReportTermType']

            try:
                resp_json = json.loads(response.text, encoding='utf-8')
                bizType_title, ind_name = self.r.get(ticker).split(";")

                if resp_json[0] == []:
                    self.logger.info(
                        f'DONE ALL PAGES OF {report_type} FOR TICKER {ticker}')
                else:
                    # Writing local data files
                    save_jsonfile(
                        resp_json, filename=f'schemaData/{self.name}/{bizType_title}_{ind_name}_{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json')
                    
                    # save_jsonfile(
                    #     resp_json, filename=f'localData/{self.name}/{ticker}_{report_type}_{report_terms[report_term]}_Page_{page}.json')
                    
                    # ES push task
                    # handleES_task.delay(self.name.lower(), ticker, resp_json, report_type)

                    # Remove error items and crawl next page
                    self.r.srem(self.error_set_key,
                                f'{ticker};{page};{report_type}')
                    # next_page = str(int(page) + 1)
                    # self.r.lpush(f'{self.name}:tickers', f'{ticker};{next_page};{report_type}')
            except Exception as e:
                self.logger.info(f'Exception: {e}')
                self.r.sadd(self.error_set_key,
                            f'{ticker};{page};{report_type}')
