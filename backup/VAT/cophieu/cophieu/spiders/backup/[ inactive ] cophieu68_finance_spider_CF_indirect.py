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
    exc_type, exc_value, exc_traceback = sys.exc_info ()
    err_details = repr (traceback.format_exception (exc_type, exc_value, exc_traceback))
    error_dict = dict (error_Name=err_details, ticker=response.meta["ticker"])
    return error_dict


def extract_tickers(tickerfile):
    tickers_list = []
    with open (tickerfile, encoding="utf-8") as jsonfile:
        text = json.load (jsonfile)
        for line in text:
            ticker = line["stockname"]
            if ticker != "000001.SS" and ticker.find ("^") == -1:
                tickers_list.append (line["stockname"])
        return tickers_list


def get_quarter_data(response, account, i, quarter_dict):
    quarters_data = response.xpath("(//td/descendant-or-self::*[contains(., $account)])[1]/following-sibling::td"
                                   , account=account)
    text_value = quarters_data[i].xpath ('string()').extract()[0]
    try:

        quarter_dict["cash flow status"][account] = int (text_value.replace (",", "").replace ("(", "")
                                                          .replace (")", ""))
    except:
        quarter_dict["cash flow status"][account] = "N/A"


ACCOUNTS = ["Net profit before tax",
            "Adjustments",
            "Depreciation and amortisation",
            "Provisions",
            "Net profit from investment in joint venture",
            "Write off fixed assets",
            "Unrealised foreign exchange profit(loss)",
            "Profit(Loss) from disposals of fixed assets",
            "Profit(Loss) from investing activities",
            "Profit from deposit",
            "Interest income",
            "Interest expense",
            "Payments direct from profit",
            "Operating profit before working capital changes",
            "Increase/decrease in receivables",
            "Increase/decrease in inventories",
            "Increase/decrease in payables",
            "Increase/decrease in pre-paid expense",
            "Increase/decrease in current assets",
            "Interest paid",
            "Business income tax paid",
            "Other payments from oprerating activities",
            "Net cashflow from operating activities",
            "Purchases of fixed assets",
            "Payment for investment in joint venture",
            "Purchases of short-term investment",
            "Investment in other entities",
            "Proceeds from disinvestment in other entities",
            "Profit from deposit received",
            "Purchases of buying minority equity",
            "Net cashflow from investing activities",
            "Purchase issued shares from other entities",
            "Repayments of financial lease",
            "Other purchase from financing activitie",
            "Purchase from capitalization issue",
            "Dividends paid",
            "Minority equity in joint venture",
            "Social welfare expenses",
            "Net cashflow of the year",
            "Effect of foreign exchange differences"]


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_CF_indirect"
    year_dict = {}
    indirect_list = []
    errors_dict = {}

    def start_requests(self):
        tickers_list = extract_tickers("tickerz.json")

        for ticker in tickers_list:
            request = scrapy.Request ('http://www.cophieu68.vn/incomestatement.php?id={0}&view=cf&year=0&lang=en'
                                      .format (ticker), callback=self.parse)
            request.meta["ticker"] = ticker
            yield request

        with open ("direct_CF_list.json", "w") as indirect_file:
            json.dump (self.indirect_list, indirect_file, indent=INDENT)

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }

        cash_flow_type = response.xpath ("//tr[@class='tr_header']/td/text()").extract ()[0]

        # EXTRACT YEAR LIST
        if cash_flow_type != "Cash Flow Direct":
            try:
                for i, year in enumerate (response.xpath ("//tr[@class=\"tr_header\"]//td/text()").extract ()[1:]):

                    quarter_dict = {"quarter": year,
                                    "cash flow status": {}
                                    }

                    for account in ACCOUNTS:
                        get_quarter_data (response, account=account, i=i, quarter_dict=quarter_dict)

                    result["data"].append (quarter_dict)

                filename = "CF_data_{0}.json".format (result["ticker"])
                file_path = make_directory (FINANCE_PATH, filename)
                with open (file_path, 'w') as fp:
                    json.dump (result, fp, indent=INDENT)

            except Exception:
                error_data = handle_error (response)
                with open ("cophieu68_CF_indirect_error_{0}.json".format (response.meta["ticker"]), "w") as error_file:
                    json.dump (error_data, error_file, indent=INDENT)

        else:
            self.indirect_list.append(response.meta["ticker"])
