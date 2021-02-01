# -*- coding: utf-8 -*-
import fad_crawl_cafef.spiders.models.constants as constants
import fad_crawl_cafef.spiders.models.utilities as utilities


name = "fin_cafef"
ticker_page_count_key = f'{name}:tp_count_cafef'
error_set_key = f'{name}:{constants.ERROR_SET_SUFFIX}'

EXAMPLE_BALANCE_SHEET_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/BSheet/2019/4/1/1/bao-cao-tai-chinh-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"

bs = [
    {"url": "https://s.cafef.vn/bao-cao-tai-chinh/{0}/BSheet/{1}/{2}/1/1/bao-cao-tai-chinh{3}",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
        },
        "meta": {
            "ticker": "",
            "year": "",
            "report_term": "",
            "report_type": "BS",
        }},
    {"url": "https://s.cafef.vn/bao-cao-tai-chinh/{0}/IncSta/{1}/{2}/1/1/ket-qua-hoat-dong-kinh-doanh{3}",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
        },
        "meta": {
            "ticker": "",
            "year": "",
            "report_term": "",
            "report_type": "IS",
        }},
    {"url": "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlow/{1}/{2}/1/1/luu-chuyen-tien-te-gian-tiep{3}",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
        },
        "meta": {
            "ticker": "",
            "year": "",
            "report_term": "",
            "report_type": "CF_Indirect",
        }},
    {"url": "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlowDirect/{1}/{2}/1/1/luu-chuyen-tien-te-truc-tiep{3}",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
        },
        "meta": {
            "ticker": "",
            "year": "",
            "report_term": "",
            "report_type": "CF_Direct",
        }}
]


log_settings = utilities.log_settings(spiderName=name,
                                      log_level="INFO",
                                      log_formatter=None
                                      )

redis_key_settings = {"REDIS_START_URLS_KEY": "%(name)s:tickers"}

concurrency_settings = {'CONCURRENT_REQUESTS': 64}

settings = {**log_settings, **redis_key_settings, **concurrency_settings}
