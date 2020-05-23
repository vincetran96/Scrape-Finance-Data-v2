# Used for crawling pdf documents for a company

### Parameters for type
# 1: bao cao tai chinh
# 23: nghi quyet hoi dong quan tri
# 8: giai trinh ket qua kinh doanh
# 9: bao cao quan tri
# 2: bao cao thuong nien (cai nay rat nang ve content/graphics)
# 4: nghi quyet dai hoi co dong
# 5: tai lieu dai hoi co dong (file rar/zip)
# 3: ban cao bach
# 10: ty le von kha dung
# 6: tai lieu khac

import functions.fad_crawl.spiders.models.constants as constants

data = {"url": "https://finance.vietstock.vn/data/getdocument",
        "formdata": {
            "code": "", # ticker
            "type": "" # document type, see above
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
