# Used for getting the list of major shareholders of a company

import functions.fad_crawl.spiders.models.constants as constants

data = {"url": "https://finance.vietstock.vn/data/shareholderdetails",
        "formdata": {
            "code": "", # ticker
            "page": constants.START_PAGE # loop until response == null
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
