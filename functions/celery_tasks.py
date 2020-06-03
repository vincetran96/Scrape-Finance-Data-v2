import time

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


### TEST AREA ###
@app.task
def adder(x, y):
    print("adding")
    time.sleep(5)
    z=x+y
    print (f'The result is {z}')
    time.sleep(5)
    return z


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
### TEST AREA ###

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
def getProxy_task():
    print ("=== GETTING PROXIES ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(getProxyHanlder)
    d = runner.join()
