# Used for crawling summarized finances (BCTT), business targets (CTKH),\
# balance sheets (CDKT), income statements (KQKD), cash flow statements (LC), financial indices (CSTC)

import functions.fad_crawl.spiders.models.constants as constants

data = {"url": "https://finance.vietstock.vn/data/financeinfo",
        "formdata": {
            "Code": "",
            "ReportType": "",
            "ReportTermType": "2",
            "Unit": "1000000",
            "Page": constants.START_PAGE,
            "PageSize": "999999999"
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
            'ticker': "",
            'ReportType': ""
        }

        }
