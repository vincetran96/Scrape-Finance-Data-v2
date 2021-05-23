
# This module contains ultilities for handling non-downloader errors and logging, used across all Spiders

import json
import logging
import os
import sys
import traceback

import redis
import scrapy.logformatter as logformatter
from scrapy.utils.request import referer_str

from scraper_vietstock.spiders.models.constants import ERROR_SET_SUFFIX


class TickerSpiderLogFormatter(logformatter.LogFormatter):
    
    def crawled(self, request, response, spider):
        return None

    def scraped(self, item, response, spider):
        return None
   
    def download_error(self, failure, request, spider, errmsg=None):
        spider_name = spider.name
        ticker = request.meta["ticker"]
        report_type = request.meta["ReportType"]
        try:
            page = request.meta["Page"]
        except:
            page = "1"

        args = {'request': request}
        msg_dict = {
            'ticker': ticker,
            'type': "Download Error",
            'message': errmsg,
        }
        msg = json.dumps(msg_dict)
        return {
            'level': logging.ERROR,
            'msg': msg,
            'args': args
        }
    
    def dropped(self, item, exception, response, spider):
        ticker = response.meta["ticker"]
        msg_dict = {
            'ticker': ticker,
            'type': "Dropped Error",
            'message': "Dropped an item...",
        }
        msg = json.dumps(msg_dict)
        return {
            'level': logging.WARNING,
            'msg': msg,
            'args': {
                'exception': exception,
                'item': item,
            }
        }

    def item_error(self, item, exception, response, spider):
        ticker = response.meta["ticker"]
        msg_dict = {
            'ticker': ticker,
            'type': "Item Error",
            'message': "There was an error in an item...",
        }
        msg = json.dumps(msg_dict)
        return {
            'level': logging.ERROR,
            'msg': msg,
            'args': {
                'item': item,
            }
        }
    
    def spider_error(self, failure, request, response, spider):
        spider_name = spider.name
        ticker = response.meta["ticker"]
        report_type = response.meta["ReportType"]
        try:
            page = response.meta["Page"]
        except:
            page = "1"

        msg_dict = {
            'ticker': ticker,
            'type': "Spider Error",
            'message': "There was an error in the spider...",
        }
        msg = json.dumps(msg_dict)
        return {
            'level': logging.ERROR,
            'msg': msg,
            'args': {
                'request': request,
                'referer': referer_str(request)
            }
        }

def log_settings(spiderName, log_level, log_formatter=None):
    '''
    log_levels: str. Can be one of these: CRITICAL, ERROR, WARNING, INFO, DEBUG
    '''
    if log_formatter:
        return {
        'LOG_ENABLED': True,
        'LOG_FILE': f'logs/{spiderName}_log_verbose.log',
        'LOG_LEVEL': log_level,
        'LOG_FORMATTER': log_formatter
    }
    else:
        return {
            'LOG_ENABLED': True,
            'LOG_FILE': f'logs/{spiderName}_log_verbose.log',
            'LOG_LEVEL': log_level
        }

# def handle_exception(spidercls, response_list=[], request_list=[]):
#     merged = response_list + request_list
#     if merged != []:
#         for r in merged:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             err_details = repr(traceback.format_exception (exc_type, exc_value, exc_traceback))
#             ticker = r.meta["ticker"]
#             url = r.url
#             error_msg = f'EXCEPTION ERROR: {err_details}; for {ticker} at {url}'
#             spidercls.logger.error(error_msg)