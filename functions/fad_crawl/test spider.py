import fad_crawl.spiders.models.utilities as utilities
import fad_crawl.spiders.models.constants as constants
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.helpers.fileDownloader import save_jsonfile
from scrapy import FormRequest
import re


TICKER = "AAA"

LANGUAGE = "en-US"
USER_COOKIE = "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBEDE986E6558A3C0BA"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

REQUESTS_LOCAL_PROXY = "127.0.0.1:8118"

vprf = {"url": "https://finance.vietstock.vn/view",
        "formdata": {
            "name": "profile",
            "code": TICKER, #ticker
        },
        "headers": {
            "User-Agent": USER_AGENT,
            "Content-Type": CONTENT_TYPE
        },
        "cookies":  {
            "language": LANGUAGE,
            "vts_usr_lg": USER_COOKIE
        },
        "meta": {
            "ticker": TICKER,
            "ReportType": "",
            "page": "1",
            "proxy": REQUESTS_LOCAL_PROXY
        }
        }



req = FormRequest(url=vprf["url"],
                           formdata=vprf["formdata"],
                           headers=vprf["headers"],
                           cookies=vprf["cookies"],
                           meta=vprf["meta"]
                           )

yield req


# view profile response
response.xpath("//div[contains(@class, 'headline')]")
response.xpath("//div[contains(@class, 'headline')]/following::table/descendant-or-self::*/text()")

for e in response.xpath("//div[contains(@class, 'headline')]"):
    s = "-".join(e.xpath("./descendant::*/text()").getall())
    t = re.sub(r'(?![- ])\W+',r' ', s).strip()
    print (t)
    print ("=========")
    s_details = "-".join(e.xpath("./following::table/descendant-or-self::*/text()").getall())
    t_details = re.sub(r'(?![- ])\W+',r' ', s_details).strip()
    # t_details = re.sub(r'(?!\b-\b|\b \b)\W+',r' ', s_details).strip()
    print (t_details.split("-"))