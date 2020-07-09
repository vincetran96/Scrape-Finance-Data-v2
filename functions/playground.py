from scrapy import FormRequest
from fad_crawl.spiders.models.financeinfo import data as fi
from fad_crawl.spiders.models.financeinfo import *
from scraper_api import ScraperAPIClient

client = ScraperAPIClient(scraper_api_key)

url_link = "https://finance.vietstock.vn/data/financeinfo"

URL = "http://api.scraperapi.com/?api_key=" + scraper_api_key + "&url=" + url_link
URL1 = client.scrapyGet(url = url_link)


ticker = "AAA"
report_type = "CDKT"

fi["formdata"]["Code"] = ticker
fi["formdata"]["ReportType"] = report_type
fi["meta"]["ticker"] = ticker
fi["meta"]["ReportType"] = report_type

# r = FormRequest(url=URL1,
#             formdata=fi["formdata"],
#             headers=fi["headers"],
#             cookies=fi["cookies"],
#             meta=fi["meta"],
#             )
