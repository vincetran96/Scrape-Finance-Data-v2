# -*- coding: utf-8 -*-
# This module contains constants used in Spiders

import os
from dotenv import load_dotenv


load_dotenv(os.path.join("", ".env"))

try:
    proxy = os.getenv('PROXY')
except:
    proxy = None

try:
    redis_host = os.getenv('REDIS_HOST')
except:
    redis_host = None

try:
    torproxy_host = os.getenv('TORPROXY_HOST')
except:
    torproxy_host = None

try:
    ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
except:
    ELASTICSEARCH_HOST = "localhost"

LANGUAGE = "en-US"
USER_COOKIE = "56CC0AD006E36400CFD2FA55EC95435C69B147DD7C7A80595A2908007CFBCC9EAA464085AB128AAC33DF8A34BCF1AC43FE0107A4C73B041FB7F26B19AA954EE69357C1BFFED5BD234E372CFCAE5184ACEAFD1AE84601668FC51346C5658A1506D88CD86BECDF20DC989A6A134B0C4E44"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

CAT_ID = "0"
INDUSTRY_ID = "0"
START_PAGE = "1"
PAGE_SIZE = "50"
BUSINESSTYPE_ID = "0"

SCRAPER_API_KEY = "2b55becc5b216a32c586c89b9ef50adc"

PROXIES_REDIS_KEY = "acceptedProxies"

TOR_CONTROLLER_PASSWORD = "12345"

if proxy:
    if torproxy_host:
        PRIVOXY_LOCAL_PROXY = [f'{torproxy_host}:8118']
        REQUESTS_LOCAL_PROXY = f'{torproxy_host}:8118'
    else:
        PRIVOXY_LOCAL_PROXY = ['torproxy:8118']
        REQUESTS_LOCAL_PROXY = 'torproxy:8118'

else:
    PRIVOXY_LOCAL_PROXY = []
    REQUESTS_LOCAL_PROXY = ""

if redis_host:
    REDIS_HOST = redis_host
else:
    REDIS_HOST = 'fad-redis'

SPIDER_EXCEPTION_COUNT_SUFFIX = "spdrexception_count"
DOWNLOADER_EXCEPTION_COUNT_SUFFIX = "dwnldrexception_count"

CRAWLED_SET_SUFFIX = "crawled_set"
ERROR_SET_SUFFIX = "error_set"
