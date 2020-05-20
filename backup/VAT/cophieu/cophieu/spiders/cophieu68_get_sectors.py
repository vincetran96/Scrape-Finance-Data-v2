import scrapy
import sys
import json
import traceback
import os

TEST_LINK = "http://www.cophieu68.vn/categorylist_detail.php?category=^nganhang"

INDENT = 2


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_sectors"
    sectors_dict = {}

    def start_requests(self):
        request = scrapy.Request ("http://www.cophieu68.vn/categorylist.php", callback=self.parse)
        yield request

    def parse(self, response):
        id_list = response.xpath("//tr[@onmouseover='hoverTR(this)']/td/a/@id").extract()
        with open("sector_codes.json", "w") as writefile:
            json.dump(id_list, writefile, indent=INDENT)

        # TODO: FOR SECTOR ID IN id_list, CRAWL A NEW PAGE (LIKE TEST_LINK)
        for sector_id in id_list:
            sector_request = scrapy.Request("http://www.cophieu68.vn/categorylist_detail.php?category=" + sector_id,
                                            callback=self.parse_tickers)
            sector_request.meta["sector"] = sector_id
            yield sector_request

    def parse_tickers(self, response):
        self.sectors_dict[response.meta["sector"]] = response.xpath("//tr[@onmouseover='hoverTR(this)']/\
                                                                    descendant::strong/text()").extract ()
        with open("sector_tickers.json", "w") as writefile2:
            json.dump(self.sectors_dict, writefile2, indent=INDENT)