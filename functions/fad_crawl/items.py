# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FadCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PDFDocItem(scrapy.Item):
    '''The PDFDocItem is a combination of a ticker and its PDF report type.
    It may contain urls to many documents from the same combination.
    See module fad_crawl.spiders.models.pdfdocs for more details.
    '''

    file_urls = scrapy.Field()
    files = scrapy.Field()
    # ticker = scrapy.Field()
    # doc_type = scrapy.Field()
