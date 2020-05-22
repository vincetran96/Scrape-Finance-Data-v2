# Used for getting the list of all companies

import functions.fad_crawl.spiders.models.constants as constants

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
        }
        }
