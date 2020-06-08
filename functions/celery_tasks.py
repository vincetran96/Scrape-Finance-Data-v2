# -*- coding: utf-8 -*-
# This module defines all tasks for the Celery app

import time

from celery import Celery
from crochet import setup
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import fad_crawl.helpers.fileDownloader as downloader
from celery_main import app
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.main import corporateazHandler
from fad_crawl.spiders.pdfDocs import pdfDocsHandler
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.pdfDocs import pdfDocsHandler
from fad_crawl.spiders.associatesDetails import associatesHandler
from fad_crawl.spiders.boardDetails import boardDetailsHandler
from fad_crawl.spiders.majorShareHolders import majorShareHoldersHandler
from fad_crawl.spiders.ownerStructure import ownerStructureHandler


### TEST AREA ###
@app.task
def adder(x, y):
    print("adding")
    time.sleep(5)
    z = x+y
    print(f'The result is {z}')
    time.sleep(5)
    return z

@app.task
def multiplier(x, y):
    print("multiplying")
    z = x*y
    print(z)

@app.task
def subtractor(x, y):
    print("subtracting")
    z = x-y
    print(z)
### TEST AREA ###

@app.task
def corporateAZ_task():
    print("=== CORPORATEAZ SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(corporateazHandler)
    d = runner.join()

@app.task
def finance_task():
    print("=== FINANCE SPIDERS CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(financeInfoHandler)
    runner.crawl(associatesHandler)
    runner.crawl(boardDetailsHandler)
    runner.crawl(majorShareHoldersHandler)
    runner.crawl(ownerStructureHandler)
    d = runner.join()
    # d_main.addBoth(lambda _: reactor.stop())
    # reactor.run()

@app.task
def pdfDocs_task(url="", filename=""):
    print("=== PDFDOCS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(pdfDocsHandler)
