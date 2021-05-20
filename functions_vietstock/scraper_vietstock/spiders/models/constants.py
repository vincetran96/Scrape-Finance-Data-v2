
# This module contains constants used in Spiders

import os
from dotenv import load_dotenv


# Attempt to load env vars
load_dotenv(os.path.join("", ".env"))

# Proxy constants
try:
    proxy = os.getenv('PROXY')
except:
    proxy = None

try:
    torproxy_host = os.getenv('TORPROXY_HOST')
except:
    torproxy_host = None

if proxy:
    if torproxy_host:
        PRIVOXY_LOCAL_PROXY = [f'{torproxy_host}:8118']
        REQUESTS_LOCAL_PROXY = f'{torproxy_host}:8118'
    else:
        PRIVOXY_LOCAL_PROXY = ["torproxy:8118"]
        REQUESTS_LOCAL_PROXY = "torproxy:8118"
else:
    PRIVOXY_LOCAL_PROXY = []
    REQUESTS_LOCAL_PROXY = ""

# Redis constants
REDIS_PORT = 6379
try:
    REDIS_HOST = os.getenv('REDIS_HOST')
except:
    REDIS_HOST = "scraper-redis"

# User cookie
try:
    USER_COOKIE = os.getenv('USER_COOKIE')
except:
    USER_COOKIE = "B213D0C1C412BAF6B9A98B01E15B24B4A96EF0DD8B304081F90B2037575928AA32A9894F659F062390AB8F5DBF85DDCC2963FA6BCF4DF4C57D0E7578BF28313D1F0C5244256999EE20387D2E9D242CC90DE788C3E32E015B04C27DDE39136EBF99778E288C0D265B806304A3CC1C7185"

# Other constants
LANGUAGE = "en-US"
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

SPIDER_EXCEPTION_COUNT_SUFFIX = "spdrexception_count"
DOWNLOADER_EXCEPTION_COUNT_SUFFIX = "dwnldrexception_count"

CRAWLED_SET_SUFFIX = "crawled_set"
ERROR_SET_SUFFIX = "error_set"

# try:
#     ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
# except:
#     ELASTICSEARCH_HOST = "localhost"