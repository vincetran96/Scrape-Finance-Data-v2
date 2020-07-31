# -*- coding: utf-8 -*-
import fad_crawl_cafef.spiders.models.constants as constants


name = "BS_cafef"
ticker_page_count_key = f'{name}:tp_count_cafef'
error_set_key = f'{name}:{constants.ERROR_SET_SUFFIX}'

bs = {"url": "https://s.cafef.vn/bao-cao-tai-chinh/{0}/BSheet/{1}/{2}/1/1/bao-cao-tai-chinh{3}",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE,
        },
        "cookies": {
        },
        "meta": {
            "ticker": "",
            "report_type": "",
            "page": "",
            "report_term": "",
        }}

settings = {}
