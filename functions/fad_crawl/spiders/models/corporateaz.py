# -*- coding: utf-8 -*-
# This module contains settings for corporateAZ Spider

# catID: san giao dich (HOSE: 1, HNX: 2, etc.)
# industryID: chon nganh (danh sach co the duoc lay tu request Industry List (category 1) tren Postman
# businessTypeID: loai hinh doanh nghiep (danh sach lay tu request Business Type for Corporate A-Z) tren Postman
# type: tabs (A-Z, Danh sach CK dang NY/GD, Niem yet moi/DKGD moi, etc.)

import redis

import functions.fad_crawl.spiders.models.constants as constants
import functions.fad_crawl.spiders.models.utilities as utilities
from functions.fad_crawl.spiders.models.financeinfo import name as financeInfo_name
from functions.fad_crawl.spiders.models.pdfdocs import name as pdfDocs_name
from functions.fad_crawl.spiders.models.associateds import name as associateds_name
from functions.fad_crawl.spiders.models.boarddetails import name as boarddetails_name
from functions.fad_crawl.spiders.models.majorshareholders import name as majorshareholders_name

r = redis.Redis(decode_responses=True)

name = "corporateAZ"

tickers_redis_keys = [f'{financeInfo_name}:tickers',
                      f'{pdfDocs_name}:tickers',
                      f'{associateds_name}:tickers',
                      f'{boarddetails_name}:tickers',
                      f'{majorshareholders_name}:tickers']

scraper_api_key = constants.SCRAPER_API_KEY

data = {"url": "https://finance.vietstock.vn/data/corporateaz",
        "formdata": {
            "catID": constants.CAT_ID,
            "industryID": constants.INDUSTRY_ID,
            "page": constants.START_PAGE,
            "pageSize": constants.PAGE_SIZE,
            "type": "0",
            "code": "",
            "businessTypeID": constants.BUSINESSTYPE_ID,
            "orderBy": "Code",
            "orderDir": "ASC"
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies":  {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        },
        "meta": {
            'pageid': "",
        },
        "proxies": {
            "http": constants.PRIVOXY_LOCAL_PROXY,
            "https": constants.PRIVOXY_LOCAL_PROXY,
        }
        }      

log_settings = utilities.log_settings(spiderName=name,
                                      log_level = "INFO")

middlewares_settings={
    'DOWNLOADER_MIDDLEWARES': {
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    }
}

proxy_settings = {
    # 'ROTATING_PROXY_LIST': r.lrange(constants.PROXIES_REDIS_KEY, 0, -1)
    'ROTATING_PROXY_LIST': [constants.PRIVOXY_LOCAL_PROXY],
    # 'ROTATING_PROXY_LIST': [],
}

settings = {**log_settings, **middlewares_settings, **proxy_settings}
