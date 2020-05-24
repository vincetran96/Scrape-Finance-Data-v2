# Used to crawl the top 2 industry levels of a company

import functions.fad_crawl.spiders.models.constants as constants

data = {"url": "https://finance.vietstock.vn/data/financeinfoCTKH",
        "formdata": {
            "Code": "", # ticker
            "ReportType": "CTKH",
            "ReportTermType": "3", # this doesn't seem to matter
            "Unit": "1000000",
            "Page": constants.START_PAGE,
            "PageSize": "1"
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies": {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        }
