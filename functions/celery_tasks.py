from billiard.context import Process
from celery import Celery
from crochet import setup
from scrapy import signals
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from celery_main import app
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.getProxy import getProxyHanlder
from fad_crawl.spiders.main import corporateazHandler
from fad_crawl.spiders.pdfDocs import pdfDocsHandler


@app.task
def adder(x, y):
    print("adding")
    z=x+y
    print (z)


@app.task
def multiplier(x, y):
    print ("multiplying")
    z=x*y
    print (z)


@app.task
def subtractor(x, y):
    print ("subtracting")
    z=x-y
    print (z)


@app.task
def corporateAZ_task():
    print ("=== CORPORATEAZ CRAWLING ===")
    setup()
    configure_logging()
    runner_main = CrawlerRunner()
    runner_main.crawl(corporateazHandler)
    d_main = runner_main.join()


@app.task
def finance_task():
    print ("=== FINANCE SPIDERS CRAWLING ===")
    setup()
    configure_logging()
    runner_main = CrawlerRunner()
    runner_main.crawl(financeInfoHandler)
    d_main = runner_main.join()
    # d_main.addBoth(lambda _: reactor.stop())
    # reactor.run()


@app.task
def get_proxy_task():
    print ("=== GETTING PROXIES ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(getProxyHanlder)
    d = runner.join()


class CrawlerProcess(Process):
    def __init__(self, spider):
        super(CrawlerProcess, self).__init__()
        setup()
        settings = get_project_settings()
        self.crawler = Crawler(spider, settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        reactor.run()


@app.task
def crawl_spider_getProxy(*args, **kwargs):
    crawler = CrawlerProcess(getProxyHanlder)
    crawler.start()
    crawler.join()

@app.task
def crawl_spider_corpAZ(*args, **kwargs):
    crawler = CrawlerProcess(corporateazHandler)
    crawler.start()
    crawler.join()

@app.task
def crawl_spider_finInfo(*args, **kwargs):
    crawler = CrawlerProcess(financeInfoHandler)
    crawler.start()
    crawler.join()
