# -*- coding: utf-8 -*-
# This module contains the stats for ticker-level Spiders

from scrapy.downloadermiddlewares.stats import DownloaderStats
from scrapy.utils.python import global_object_name


class TickerCrawlerStats(DownloaderStats):
    def __init__(self, stats):
        self.stats = stats

    def process_exception(self, request, exception, spider):
        ex_class = global_object_name(exception.__class__)
        ticker = request.meta["ticker"]
        self.stats.inc_value('downloader/exception_count', spider=spider)
        self.stats.inc_value('downloader/exception_type_count/%s' % ex_class, spider=spider)
        self.stats.set_value(f'downloader/my_errors/{ticker}', ex_class)
