import logging
import os
import sys
import traceback
import json

import scrapy.logformatter as logformatter
from scrapy.utils.request import referer_str


class TickerSpiderLogFormatter(logformatter.LogFormatter):
    
    def crawled(self, request, response, spider):
        return None

    def scraped(self, item, response, spider):
        return None
   
    def download_error(self, failure, request, spider, errmsg=None):
        ticker = request.meta["ticker"]
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
            'message': "Dropped somethin...g",
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
            'message': "Item something...",
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
        ticker = response.meta["ticker"]
        msg_dict = {
            'ticker': ticker,
            'type': "Spider Error",
            'message': "Spider something...",
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


def handle_exception(spidercls, response_list=[], request_list=[]):
    merged = response_list + request_list
    if merged != []:
        for r in merged:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_details = repr(traceback.format_exception (exc_type, exc_value, exc_traceback))
            ticker = r.meta["ticker"]
            url = r.url
            error_msg = f'EXCEPTION ERROR: {err_details}; for {ticker} at {url}'
            spidercls.logger.error(error_msg)

def log_settings(spiderName, log_level, log_formatter=None):
    # log_level: CRITICAL, ERROR, WARNING, INFO, DEBUG
    if log_formatter:
        return {
        'LOG_ENABLED': True,
        'LOG_FILE': f'logs/{spiderName}_errors_long.log',
        'LOG_LEVEL': log_level,
        'LOG_FORMATTER': log_formatter
    }
    else:
        return {
            'LOG_ENABLED': True,
            'LOG_FILE': f'logs/{spiderName}_errors_long.log',
            'LOG_LEVEL': log_level
        }

# if __name__ == "__main__":
#     crawl_main()
#     crawl_test()
