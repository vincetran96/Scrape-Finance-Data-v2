import fad_crawl.spiders.models.utilities as utilities
import fad_crawl.spiders.models.constants as constants
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.helpers.fileDownloader import save_jsonfile

# TESTING FOR VIEWPROFILE HTM WITH XPATH
from scrapy import FormRequest
import re


TICKER = "AAA"

LANGUAGE = "en-US"
USER_COOKIE = "56CC0AD006E36400CFD2FA55EC95435C69B147DD7C7A80595A2908007CFBCC9EAA464085AB128AAC33DF8A34BCF1AC43FE0107A4C73B041FB7F26B19AA954EE69357C1BFFED5BD234E372CFCAE5184ACEAFD1AE84601668FC51346C5658A1506D88CD86BECDF20DC989A6A134B0C4E44"
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


# June 30, 2020
response.xpath("//h4/text()").getall()
for s in response.xpath("//h4/descendant-or-self::*/text()").getall():
    if s.strip() != "":
        heading = s.strip()
        