import scrapy
import sys
import json
import traceback
import os

FINANCE_PATH = "income_statements/"

INDENT = 2


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


def get_quarter_data(response, account, i, quarter_dict):
    quarters_data = response.xpath ("//td/descendant-or-self::*[contains(., $account)]/parent::tr/td[@align='right']/\
                                    descendant-or-self::*/text()", account=account).extract ()
    try:
        quarter_dict["income status"][account] = int (quarters_data[i].replace (",", "").replace ("(", "")
                                                      .replace (")", ""))
    except:
        try:
            quarter_dict["income status"][account] = float ("{0}".format (quarters_data[i].replace (",", ""))
                                                            .replace ("(", "").replace (")", ""))
        except:
            quarter_dict["income status"][account] = "{0}".format(quarters_data[i].replace (",", "")).replace ("(", "")\
                                                                    .replace (")", "")


ACCOUNTS = ["Net sales",
            "Cost of goods sold",
            "Gross Profit",
            "Financial expenses",
            "Of which: Interest expense",
            "Cost of sales",
            "Enterprise cost management",
            "Total Operating Expenses",
            "Total revenue financing activities",
            "Net profit from business activities",
            "Profit",
            "Profit before tax",
            "Present corporate income tax expenses",
            "Deferred income taxes expenses",
            "The interests of minority shareholders",
            "Total Cost of profits",
            "Profit after tax corporate income",
            "Volume",
            "Close of Quarter",
            "EPS",
            "PE",
            "Book Price"]


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_IS"
    year_dict = {}
    errors = []

    def start_requests(self):
        tickers_list = []
        with open ("tickerz.json", encoding="utf-8") as jsonfile:
            text = json.load (jsonfile)
            for line in text:
                ticker = line["stockname"]
                if ticker != "000001.SS" and ticker.find ("^") == -1:
                    tickers_list.append (line["stockname"])

        for ticker in tickers_list:
            request = scrapy.Request (
                'http://www.cophieu68.vn/incomestatement.php?id={0}&view=ist&year=0&lang=en'.format (ticker),
                callback=self.parse)
            request.meta["ticker"] = ticker
            yield request

        with open("cophieu68_IS_errors.json", "w") as error_file:
            json.dump(self.errors, error_file, indent=INDENT)

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }
        try:
            for i, quarter in enumerate (response.xpath ("//tr[@class=\"tr_header\"]//td/text()").extract ()[1:]):

                quarter_dict = {"quarter": quarter,
                                "income status": {}
                                }

                for account in ACCOUNTS:
                    get_quarter_data (response, account=account, i=i, quarter_dict=quarter_dict)

                result["data"].append(quarter_dict)

            filename = "IS_data_{0}.json".format (result["ticker"])
            file_path = make_directory (FINANCE_PATH, filename)
            with open (file_path, 'w') as fp:
                json.dump (result, fp, indent=INDENT)

        except Exception:
            error_data = handle_error (response)
            self.errors.append(error_data)