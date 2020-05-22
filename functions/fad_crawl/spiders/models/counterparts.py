# Used for getting the list of companies in the same industry

import functions.fad_crawl.spiders.models.constants as constants

count_data = {"url": "https://finance.vietstock.vn/company/GetCountCompanyRelation",
        "formdata": {
            "code": "", # ticker
            "tradingdate": "", # YYYY-MM-DD
            "exchangeID": ""
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies":  {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        }
        }

find_data = {"url": "https://finance.vietstock.vn/company/GetCompanyRelationFilter",
        "formdata": {
            "code": "", # ticker
            "Page": constants.START_PAGE,
            "PageSize": "", # can be equal to result of the count above
            "ToDate": "", # YYYY-MM-DD
            "ExchangeID": "",
            "OrderBy": "0",
            "Direction": ""
        },
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Content-Type": constants.CONTENT_TYPE
        },
        "cookies":  {
            "language": constants.LANGUAGE,
            "vts_usr_lg": constants.USER_COOKIE
        }
        }
