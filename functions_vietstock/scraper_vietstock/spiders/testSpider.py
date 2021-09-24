import scrapy
from scraper_vietstock.spiders.models.testspider import name


class testSpider(scrapy.Spider):
    name = name
    start_urls = [
        "www.google.com",
        "www.example.com",
        "www.qiwjedasdhaskdh.com"
    ]

    def parse(self, response, **kwargs):
        pass
