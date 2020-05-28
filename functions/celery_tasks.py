from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from celery_main import app
from crochet import setup
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.main import corporateazHandler
from fad_crawl.spiders.pdfDocs import pdfDocsHandler
from celery import Celery


@app.task
def adder(x, y):
    print("calculating")
    return x+y


@app.task
def crawl_task():
    print ("=== CRAWL TASK IS RUNNING ===")
    setup()
    configure_logging()
    runner_main = CrawlerRunner()
    runner_main.crawl(corporateazHandler)
    runner_main.crawl(financeInfoHandler)
    d_main = runner_main.join()
    # d_main.addBoth(lambda _: reactor.stop())
    # reactor.run()


@app.task
def crawl_test():
    runner_test = CrawlerRunner()
    runner_test.crawl(financeInfoHandler)
    # runner_test.crawl(pdfDocsHandler)
    d = runner_test.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
