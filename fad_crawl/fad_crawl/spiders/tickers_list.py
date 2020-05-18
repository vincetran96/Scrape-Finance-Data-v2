# -*- coding: utf-8 -*-
# This spider crawls the list of company names on Vietstock

import scrapy
from scrapy import FormRequest

LANGUAGE = "vi-VN"
USER_COOKIE = "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBEDE986E6558A3C0BA"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"


class ExampleSpider(scrapy.Spider):
    name = 'tickers_list'

    def start_requests(self):
        req_tl = FormRequest(url="https://finance.vietstock.vn/data/corporateaz",
                          formdata={
                              "catID": "0",
                              "industryID": "0",
                              "page": "150",
                              "pageSize": "20",
                              "type": "0",
                              "code": "",
                              "businessTypeID": "0",
                              "orderBy": "Code",
                              "orderDir": "ASC"
                          },
                          headers={
                              "User-Agent": USER_AGENT,
                              "Content-Type": CONTENT_TYPE
                          },
                          cookies={
                              "language": LANGUAGE,
                              "vts_usr_lg": USER_COOKIE
                          },
                          callback=self.parse)
        yield req_tl

    def parse(self, response):
        print(response.text)
