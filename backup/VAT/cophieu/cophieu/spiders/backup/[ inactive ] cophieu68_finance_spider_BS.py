import scrapy
import sys
import json
import traceback
import os

FINANCE_PATH = "balance_sheets/"

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


class QuotesSpider (scrapy.Spider):
    name = "finance_BS"
    year_dict = {}

    def start_requests(self):
        tickers_list = []
        with open ('copyy.json', encoding="utf-8") as jsonfile:
            text = json.load (jsonfile)
            for line in text:
                ticker = line["stockname"]
                if ticker != "000001.SS" and ticker.find ("^") == -1:
                    tickers_list.append (line["stockname"])

        for ticker in tickers_list:
            request = scrapy.Request (
                'http://www.cophieu68.vn/incomestatement.php?id={0}&view=bs&year=0&lang=en'.format (ticker),
                callback=self.parse)
            request.meta["ticker"] = ticker
            yield request

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }

        asset_accounts = ["Cash and cash equivalents",
                          "Short-term financial investments",
                          "The short-term receivables",
                          "Inventory",
                          "Other short-term assets",
                          "The long-term receivables",
                          "Fixed assets",
                          "(Accumulated depreciation)",
                          "Real Estate Investment",
                          "Long-term financial investments",
                          "Total other long-term assets",
                          "Goodwill",
                          "TOTAL ASSETS"]

        liabs_accounts = ["Short-term debt",
                          "Long-term debt",
                          "Total Debt"]

        capital_accounts = ["Equity",
                            "Funds and other funds",
                            "Total Sources of Funds",
                            "The interests of minority shareholders"]

        # EXTRACT YEAR LIST
        try:
            for i, year in enumerate (response.xpath ("//tr[@class=\"tr_header\"]//td/text()").extract ()[1:]):

                year_data = {"year": year,
                             "assets": {},
                             "liabilities": {},
                             "sources of capital": {}
                             }

                for asset_account in asset_accounts:
                    if asset_account == "TOTAL ASSETS":
                        years_data = response.xpath ("//td/descendant-or-self::*[contains(., $account)]/parent::tr",
                                                     account=asset_account)[1].xpath (".//td[@align='right']/\
                                                     descendant-or-self::*/text()").extract ()
                    else:
                        years_data = response.xpath ("//td/descendant-or-self::*[contains(., $account)]/parent::tr/\
                                                    td[@align='right']/descendant-or-self::*/text()",
                                                     account=asset_account).extract ()
                    try:
                        year_data["assets"][asset_account] = int (years_data[i].replace (",", ""))
                    except:
                        year_data["assets"][asset_account] = years_data[i].replace (",", "")

                for liabs_account in liabs_accounts:
                    years_data = response.xpath ("//td/descendant-or-self::*[contains(., $account)]/parent::tr/\
                                                td[@align='right']/descendant-or-self::*/text()",
                                                 account=liabs_account).extract ()
                    try:
                        year_data["liabilities"][liabs_account] = int (years_data[i].replace (",", ""))
                    except:
                        year_data["liabilities"][liabs_account] = years_data[i].replace (",", "")

                for capital_account in capital_accounts:
                    years_data = response.xpath ("//td/descendant-or-self::*[contains(., $account)]/parent::tr/\
                                                td[@align='right']/descendant-or-self::*/text()",
                                                 account=capital_account).extract ()
                    try:
                        year_data["sources of capital"][capital_account] = int (years_data[i].replace (",", ""))
                    except:
                        year_data["sources of capital"][capital_account] = years_data[i].replace (",", "")

                result["data"].append (year_data)

            filename = "BS_data_{0}.json".format (result["ticker"])
            file_path = make_directory (FINANCE_PATH, filename)
            with open (file_path, 'w') as fp:
                json.dump (result, fp, indent=INDENT)

        except Exception:
            error_data = handle_error (response)
            with open ("error_{0}.json".format (response.meta["ticker"]), "w") as error_file:
                json.dump (error_data, error_file, indent=INDENT)
