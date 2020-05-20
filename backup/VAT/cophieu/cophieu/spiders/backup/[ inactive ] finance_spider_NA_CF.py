import scrapy
import sys
import json
import traceback
import os

FINANCE_PATH = "NA_CFs/"

INDENT = 2

H = "http://s.cafef.vn/bao-cao-tai-chinh/"
CF_CODE = "CashFlowDirect/"
YEARS = ["2012", "2013", "2014", "2015", "2016"]
QUARTER = "4/"
IDX = "0/"
SHOWTYPE = "1/"
OPTION = "0/"
CF = "luu-chuyen-tien-te-truc-tiep-"

ACCOUNTS = ['Tiền thu từ bán hàng, cung cấp dịch vụ và doanh thu khác',
            'Tiền chi trả cho người cung cấp hàng hóa và dịch vụ',
            'Tiền chi trả cho người lao động',
            'Tiền chi trả lãi vay',
            'Tiền chi nộp thuế thu nhập doanh nghiệp',
            'Tiền thu khác từ hoạt động kinh doanh',
            'Tiền chi khác cho hoạt động kinh doanh',
            'Lưu chuyển tiền thuần từ hoạt động kinh doanh',
            'Tiền chi để mua sắm, xây dựng tài sản cố định',
            'Tiền thu do thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác',
            'Tiền chi cho vay, mua các công cụ nợ của đơn vị khác',
            'Tiền thu hồi cho vay, bán lại công cụ nợ của đơn vị khác',
            'Tiền chi đầu tư góp vốn vào đơn vị khác',
            'Tiền thu do bán các khoản đầu tư góp vốn vào đơn vị khác',
            'Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia',
            'Tiền đầu tư xây dựng nhà xưởng',
            'Tăng lợi ích của cổ đông thiếu số khi hợp nhất công ty con',
            'Loại trừ lợi ích của cổ đông thiểu số khi thanh lý công ty con',
            'Tiền mặt tại công ty con mua trong năm',
            'Tiền thu do nhượng bán các khoản đầu tư vào công ty con',
            'Tiền chi gửi ngắn hạn',
            'Tiền thu lãi từ gửi ngắn hạn',
            'Tiền chi mua tài sản khác',
            'Giảm tiền gửi ngân hàng có kỳ hạn',
            'Tiền chi để mua thêm cổ phần của công ty con',
            'Tiền thu từ các khoản ký gửi, ký quỹ dài hạn',
            'Tiền gửi ngắn hạn',
            'Rút tiền gửi ngắn hạn',
            'Tiền thu từ chuyển quyền góp vốn vào dự án',
            'Lưu chuyển tiền thuần từ hoạt động đầu tư',
            'Tiền thu từ phát hành cổ phiếu, nhận góp vốn của chủ sở hữu',
            'Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp của doanh nghiệp đã phát hành',
            'Tiền thu từ nhận góp vốn liên doanh',
            'Tiền vay ngắn hạn, dài hạn nhận được',
            'Tiền chi trả nợ gốc vay',
            'Tiền chi trả nợ thuê tài chính',
            'Tiền chi cho đầu tư ngắn hạn',
            'Cổ tức, lợi nhuận đã trả cho chủ sở hữu',
            'Cổ tức, lợi nhuận đã trả cho cổ đông thiểu số',
            'Nhận vốn góp của cổ đông thiểu số',
            'Chi khác từ lợi nhuận chưa phân phối',
            'Tiền thu từ lãi tiền gửi',
            'Lưu chuyển tiền thuần từ/(sử dụng vào) hoạt động tài chính',
            'Lưu chuyển tiền thuần trong năm']


def make_directory(path, filename):
    path_to_file = path + filename
    if not os.path.exists (path_to_file):
        os.makedirs (os.path.dirname (path_to_file), exist_ok=True)
    return path_to_file


def handle_error(response):
    exc_type, exc_value, exc_traceback = sys.exc_info ()
    err_details = repr (traceback.format_exception (exc_type, exc_value, exc_traceback))
    error_dict = dict (error_Name=err_details, ticker=response.meta["ticker"])
    return error_dict


class FinanceSpider (scrapy.Spider):
    name = "finance_NA_CF"
    dicter = {}

    def start_requests(self):
        with open ("NA_list.json", encoding="utf-8") as jsonfile:
            text = json.load (jsonfile)
            for ticker, company_name in text.items ():
                company_query = company_name.replace (" ", "-")
                result = {"ticker": ticker,
                          "data": []}
                self.dicter[ticker] = {}
                for year in YEARS:
                    self.dicter[ticker][year] = []
                    request_url = H + ticker + "/" + CF_CODE + year + "/" + QUARTER + IDX + SHOWTYPE + CF + \
                                  company_query + ".chn"
                    request = scrapy.Request (request_url, callback=self.parse)
                    request.meta['ticker'] = ticker
                    request.meta["year"] = year
                    yield request

                    result["data"] += self.dicter[ticker][year]

                filename = "NA_CF_data_{0}.json".format (result["ticker"])
                file_path = make_directory (FINANCE_PATH, filename)
                with open (file_path, 'w') as fp:
                    json.dump (result, fp, indent=INDENT)

    def parse(self, response):
        quarter_list = response.xpath ("//td[@class='h_t']/text()").extract ()
        # try:
        for i, quarter in enumerate (quarter_list):
            quarter_data = {"quarter": quarter,
                            "cash_flow_status": {}}
            for account in ACCOUNTS:
                try:
                    quarter_data_rp = \
                    response.xpath ("//td[contains(., $account)]/parent::tr/td[@align = 'right']/text()"
                                    , account=account).extract ()[i]
                except:
                    quarter_data_rp = "N/A"

                quarter_data["cash_flow_status"][account] = quarter_data_rp
            # print(quarter_data)
            self.dicter[response.meta["ticker"]][response.meta["year"]].append (quarter_data)
