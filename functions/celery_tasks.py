# -*- coding: utf-8 -*-
# This module defines all tasks for the Celery app

import time
import redis
import logging

from celery import Celery
from crochet import setup
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging, _get_handler
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
from fad_crawl.spiders.counterParts import counterpartsHandler
from fad_crawl.spiders.models.corporateaz import log_settings as corporateaz_settings
from fad_crawl.spiders.models.associatesdetails import log_settings as associatesdetails_settings
from fad_crawl.spiders.models.financeinfo import log_settings as financeinfo_settings


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
def prerun_cleanup_task():
    """ Delete all residual Redis keys
    """
    r = redis.Redis(decode_responses=True)
    for k in r.keys('*'):
        r.delete(k)

@app.task
def corporateAZ_task():
    print("=== CORPORATEAZ SPIDER CRAWLING ===")
    setup()
    configure_logging()
    
    # settings=get_project_settings()
    # settings.update(corporateaz_settings)
    # configure_logging(settings=settings, install_root_handler=False)
    # logging.root.setLevel(logging.NOTSET)
    # handler = _get_handler(settings)
    # # logging.root.removeHandler(handler)
    # logging.root.addHandler(handler)

    runner = CrawlerRunner()
    runner.crawl(corporateazHandler)
    d = runner.join()

@app.task
def finance_task():
    print("=== FINANCE SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(financeInfoHandler)
    d = runner.join()
    # d_main.addBoth(lambda _: reactor.stop())
    # reactor.run()

@app.task
def associates_task():
    print("=== ASSOCIATES SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(associatesHandler)
    d = runner.join()

@app.task
def counterparts_task():
    print("=== COUNTERPARTS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(counterpartsHandler)
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
