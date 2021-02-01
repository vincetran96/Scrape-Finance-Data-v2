# -*- coding: utf-8 -*-
# This module defines all tasks for the Celery app

import logging
import time

import redis
from celery import Celery
from crochet import setup
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import _get_handler, configure_logging
from scrapy.utils.project import get_project_settings

import corpAZ_cafef
from celery_main_cafef import app
from fad_crawl_cafef.spiders.balanceSheet_cafef import balanceSheetCafeFHandler
from fad_crawl_cafef.spiders.industriesTickers_cafef import industriesTickersCafeFHandler
from fad_crawl_cafef.spiders.models.constants import REDIS_HOST


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
    r = redis.Redis(host=REDIS_HOST, decode_responses=True)
    r.flushdb()

@app.task
def corporateAZ_cafef_task():
    print("=== CORPORATEAZ CAFEF SPIDER CRAWLING ===")
    corpAZ_cafef.run()

@app.task
def industriestickers_cafef_task():
    print("=== INDUSTRIES TICKERS CAFEF SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(industriesTickersCafeFHandler)
    d = runner.join()

@app.task
def balancesheet_cafef_task():
    print("=== BALANCE SHEET CAFEF SPIDER CRAWLING ===")
    setup()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    runner.crawl(balanceSheetCafeFHandler)
    d = runner.join()
