# BACKUP FILE
# # -*- coding: utf-8 -*-
# # This spider crawls a ticker's PDF Documents

# import json
# import os
# import sys
# import traceback
# from pprint import pprint

# import redis
# import scrapy
# from scrapy import FormRequest, Request
# from scrapy.crawler import CrawlerRunner
# from scrapy.loader import ItemLoader
# from scrapy_redis import defaults
# from scrapy_redis.spiders import RedisSpider
# from scrapy_redis.utils import bytes_to_str

# import fad_crawl.helpers.fileDownloader as pdf
# from fad_crawl.items import PDFDocItem
# from fad_crawl.spiders.models.pdfdocs import data as fi
# from fad_crawl.spiders.models.pdfdocs import name, settings, type_list


# class pdfDocsHandler(RedisSpider):
#     name = name
#     custom_settings = settings

#     def __init__(self, *args, **kwargs):
#         super(pdfDocsHandler, self).__init__(*args, **kwargs)
#         self.type_list = type_list
#         self.r = redis.Redis()
#         self.crawled_count_key = f'{self.name}:crawledcount'
#         self.dequeued_count_key = f'{self.name}:dequeuedcount'
    
#     def next_requests(self):
#         """
#         Replaces the default method. Closes spider when tickers are crawled and queue empty.
#         """
#         use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
#         fetch_one = self.server.spop if use_set else self.server.lpop
#         found = 0
#         while found < self.redis_batch_size:
#             data = fetch_one(self.redis_key)
#             if not data:
#                 break
#             for doc_type in self.type_list:
#                 req = self.make_request_from_data(data, doc_type)
#                 if req:
#                     yield req
#                     found += 1
#                     dq = self.r.incr(self.dequeued_count_key)
#                     self.logger.info(f'Dequeued {dq} ticker-reports so far')
#                 else:
#                     self.logger.info("Request not made from data: %r", data)

#         if found:
#             self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

#         if self.r.get(self.crawled_count_key) and self.r.get(self.dequeued_count_key):
#             if self.r.llen(self.redis_key) == 0 and self.r.get(self.crawled_count_key) >= self.r.get(self.dequeued_count_key):
#                 self.r.delete(self.crawled_count_key)
#                 self.r.delete(self.dequeued_count_key)
#                 self.crawler.engine.close_spider(spider=self, reason="Queue is empty, the spider closes")

#     def make_request_from_data(self, data, doc_type):
#         """
#         Replaces the default method, data is a ticker.
#         """
#         ticker = bytes_to_str(data, self.redis_encoding)

#         fi["formdata"]["code"] = ticker
#         fi["formdata"]["type"] = doc_type
#         fi["meta"]["ticker"] = ticker
#         fi["meta"]["ReportType"] = doc_type

#         return FormRequest(url=fi["url"],
#                             formdata=fi["formdata"],
#                             headers=fi["headers"],
#                             cookies=fi["cookies"],
#                             meta=fi["meta"],
#                             callback=self.parse
#                             )

#     def parse(self, response):
#         resp_json = json.loads(response.text)
#         doc_urls = [d['Url'] for d in resp_json]
#         ticker = response.meta["ticker"]
#         doc_type = response.meta["ReportType"]

#         l = ItemLoader(item=PDFDocItem(), response=response)
#         l.add_value('file_urls', doc_urls)

#         c = self.r.incr(self.crawled_count_key)
#         self.logger.info(f'Crawled {c} ticker-reports so far')

#         return l.load_item()

#         # for d in resp_json:
#         #     doc_title = d["Title"]
#         #     ticker = response.meta["ticker"]
#         #     doc_type = response.meta["ReportType"]
            
#         #     filename = f'localData/PDFs/{ticker}_{doc_type}_{doc_title}_'            
#         #     c = self.r.incr(self.crawled_count_key)
#         #     self.logger.info(f'Crawled {c} ticker-reports so far')
