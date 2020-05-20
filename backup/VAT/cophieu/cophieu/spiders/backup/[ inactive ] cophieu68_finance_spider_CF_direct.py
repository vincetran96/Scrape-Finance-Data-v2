import scrapy
import sys
import json
import traceback
import os

FINANCE_PATH = "cash_flow_statements/"

INDENT = 2


def make_directory(path, filename):
    path_to_file = path + filename
    if not os.path.exists (path_to_file):
        os.makedirs (os.path.dirname (path_to_file), exist_ok=True)
    return path_to_file


def handle_error(response):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    err_details = repr(traceback.format_exception (exc_type, exc_value, exc_traceback))
    error_dict = dict(error_Name=err_details, ticker=response.meta["ticker"])
    return error_dict


def get_quarter_data(response, account, i, quarter_dict):
    quarters_data = response.xpath ("(//td/descendant-or-self::*[contains(., $account)])[1]/following-sibling::td"
                                    , account=account)
    try:
        text_value = quarters_data[i].xpath ('string()').extract ()[0]
    except:
        text_value = "N/A"
    try:
        quarter_dict["cash flow status"][account] = int (text_value.replace (",", "").replace ("(", "")
                                                          .replace (")", ""))
    except:
        quarter_dict["cash flow status"][account] = text_value
    

ACCOUNTS = ["Tiền thu từ bán hàng, cung cấp dịch vụ và doanh thu khác",
            "Tiền chi trả cho người cung cấp hàng hóa và dịch vụ",
            "Tiền chi trả cho người lao động",
            "Tiền chi trả lãi vay",
            "Tiền chi nộp thuế thu nhập doanh nghiệp",
            "Tiền chi nộp thuế giá trị gia tăng",
            "Tiền thu khác từ hoạt động kinh doanh",
            "Tiền chi khác cho hoạt động kinh doanh",
            "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
            "Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác",
            "Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác",
            "Tiền chi cho vay, mua các công cụ nợ của các đơn vị khác",
            "Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",
            "Tiền chi đầu tư góp vốn vào đơn vị khác",
            "Tiền thu hồi đầu tư góp vốn vào đơn vị khác",
            "Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",
            "Lưu chuyển tiền thuần từ hoạt động đầu tư",
            "Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",
            "Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành",
            "Tiền vay ngắn hạn, dài hạn nhận được",
            "Tiền chi trả nợ gốc vay",
            "Tiền chi để mua sắm, xây dựng TSCĐ, BĐS đầu tư",
            "Tiền chi trả nợ thuê tài chính",
            "Cổ tức, lợi nhuận đã trả cho chủ sở hữu",
            "Chi từ các quỹ của doanh nghiệp",
            "Lưu chuyển tiền thuần từ hoạt động tài chính",
            "Lưu chuyển tiền thuần trong kỳ",
            "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ"]


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_CF_direct"
    year_dict = {}
    NA_dict = {}
    errors_dict = {}

    def start_requests(self):
        with open ("direct_CF_list.json", encoding="utf-8") as jsonfile:
            text = json.load (jsonfile)
            for ticker in text:
                request = scrapy.Request("http://www.cophieu68.vn/incomestatement.php?id={0}&view=cf&year=0%lang=vn"
                                         .format(ticker), callback=self.parse)
                request.meta["ticker"] = ticker
                yield request

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }
        try:
            for i, quarter in enumerate (response.xpath ("//tr[@class='tr_header']//td/text()").extract ()[1:]):

                quarter_dict = {"quarter": quarter,
                                "cash flow status": {},
                                }

                for account in ACCOUNTS:
                    get_quarter_data(response, account=account, i=i, quarter_dict=quarter_dict)

                result["data"].append (quarter_dict)

            filename = "CF_data_{0}.json".format (result["ticker"])
            file_path = make_directory (FINANCE_PATH, filename)
            with open (file_path, 'w') as fp:
                json.dump (result, fp, indent=INDENT)

        except:
            error_data = handle_error (response)
            with open ("cophieu68_CF_direct_error_{0}.json".format (response.meta["ticker"]), "w") as error_file:
                json.dump (error_data, error_file, indent=INDENT)


