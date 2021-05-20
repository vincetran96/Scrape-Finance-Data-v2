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

from celery_main import app
import scraper_vietstock.helpers.fileDownloader as downloader
from scraper_vietstock.spiders.financeInfo import financeInfoHandler
from scraper_vietstock.spiders.corpAZ import corporateazHandler
from scraper_vietstock.spiders.corpAZExpress import corporateazExpressHandler
from scraper_vietstock.spiders.pdfDocs import pdfDocsHandler
from scraper_vietstock.spiders.financeInfo import financeInfoHandler
from scraper_vietstock.spiders.pdfDocs import pdfDocsHandler
from scraper_vietstock.spiders.associatesDetails import associatesHandler
from scraper_vietstock.spiders.boardDetails import boardDetailsHandler
from scraper_vietstock.spiders.majorShareholders import majorShareHoldersHandler
from scraper_vietstock.spiders.ownerStructure import ownerStructureHandler
from scraper_vietstock.spiders.counterParts import counterPartsHandler
from scraper_vietstock.spiders.ctkhDetails import ctkhDetailsHandler
from scraper_vietstock.spiders.viewProfile import viewProfileHandlder
from scraper_vietstock.spiders.models.constants import REDIS_HOST


@app.task
def prerun_cleanup_task():
    ''' 
    Delete all residual Redis keys
    '''
    r = redis.Redis(host=REDIS_HOST)
    r.flushdb()

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

    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(corporateazHandler)
    d = runner.join()

@app.task
def corporateAZExpress_task():
    print("=== CORPORATEAZ-Express SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(corporateazExpressHandler)
    d = runner.join()

@app.task
def finance_task():
    print("=== FINANCE SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(financeInfoHandler)
    d = runner.join()
    # d_main.addBoth(lambda _: reactor.stop())
    # reactor.run()

@app.task
def associates_task():
    print("=== ASSOCIATES SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(associatesHandler)
    d = runner.join()

@app.task
def counterparts_task():
    print("=== COUNTERPARTS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(counterPartsHandler)
    d = runner.join()

@app.task
def majorshareholders_task():
    print("=== MAJOR SHAREHOLDERS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(majorShareHoldersHandler)
    d = runner.join()

@app.task
def ownerstructure_task():
    print("=== OWNER STRUCTURE SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(ownerStructureHandler)
    d = runner.join()

@app.task
def ctkhdetails_task():
    print("=== CTKH DETAILS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(ctkhDetailsHandler)
    d = runner.join()

@app.task
def boarddetails_task():
    print("=== BOARD DETAILS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(boardDetailsHandler)
    d = runner.join()

@app.task
def viewprofile_task():
    print("=== VIEW PROFILE SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(viewProfileHandlder)
    d = runner.join()

@app.task
def pdfDocs_task(url="", filename=""):
    print("=== PDFDOCS SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(pdfDocsHandler)