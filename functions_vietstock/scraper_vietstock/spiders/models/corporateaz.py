# -*- coding: utf-8 -*-
# This module contains settings for corporateAZ Spider

# catID: san giao dich (HOSE: 1, HNX: 2, etc.)
# industryID: chon nganh (danh sach co the duoc lay tu request Industry List (category 1) tren Postman
# businessTypeID: loai hinh doanh nghiep (danh sach lay tu request Business Type for Corporate A-Z) tren Postman
# type: tabs (A-Z, Danh sach CK dang NY/GD, Niem yet moi/DKGD moi, etc.)

import redis

import scraper_vietstock.spiders.models.constants as constants
import scraper_vietstock.spiders.models.utilities as utilities
from scraper_vietstock.spiders.models.financeinfo import name as financeInfo_name
from scraper_vietstock.spiders.models.pdfdocs import name as pdfDocs_name
from scraper_vietstock.spiders.models.associatesdetails import name as associates_name
from scraper_vietstock.spiders.models.boarddetails import name as boarddetails_name
from scraper_vietstock.spiders.models.majorshareholders import name as majorshareholders_name
from scraper_vietstock.spiders.models.counterparts import name as counterparts_name
from scraper_vietstock.spiders.models.ownerstructure import name as ownerstructure_name
from scraper_vietstock.spiders.models.ctkhdetails import name as ctkh_name
from scraper_vietstock.spiders.models.viewprofile import name as viewprofile_name


name_regular = "corporateAZ"
name_express = "corporateAZExpress"
fin_insur_tickers_key = "finance_and_insurance_tickers_total"
all_tickers_key = "all_tickers_total"

tickers_redis_keys = [
                      f'{financeInfo_name}:tickers',
                      f'{pdfDocs_name}:tickers',
                      f'{associates_name}:tickers',
                      f'{boarddetails_name}:tickers',
                      f'{majorshareholders_name}:tickers',
                      f'{counterparts_name}:tickers',
                      f'{ownerstructure_name}:tickers',
                      f'{ctkh_name}:tickers',
                      f'{viewprofile_name}:tickers'
                    ]

closed_redis_key = f'{name_regular}:closed'
bizType_ind_set_key = 'bizType_ind_set'

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
        "cookies": {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        },
        "meta": {
            "page": constants.START_PAGE,
            "TotalPages": "",
            "bizType_id": "",
            "bizType_title": "",
            "ind_id": "",
            "ind_name": "",
        }
        }

business_type = {
        "url": "https://finance.vietstock.vn/data/businesstype",
        "headers": {
            "User-Agent": constants.USER_AGENT
        },
        "cookies": {
            "language": constants.LANGUAGE
        },
        }

industry_list = {
        "url": "https://finance.vietstock.vn/data/industrylist",
        "headers": {
            "User-Agent": constants.USER_AGENT
        },
        "cookies": {
            "language": constants.LANGUAGE
        },
        "meta": {
            "bizType_id": "",
            "bizType_title": "",
        }
        }

log_settings_regular = utilities.log_settings(spiderName=name_regular,
                                      log_level = "INFO")

log_settings_express = utilities.log_settings(spiderName=name_express,
                                      log_level = "INFO")

middlewares_settings={
    'DOWNLOADER_MIDDLEWARES': {
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    }
}

proxy_settings = {
    'ROTATING_PROXY_LIST': constants.PRIVOXY_LOCAL_PROXY,
}

settings_regular = {**log_settings_regular, **middlewares_settings, **proxy_settings}
settings_express = {**log_settings_express, **middlewares_settings, **proxy_settings}
