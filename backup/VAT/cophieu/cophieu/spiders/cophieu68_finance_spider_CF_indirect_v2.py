import scrapy
import sys
import json
import traceback
import os

FINANCE_PATH = "cash_flow_statements/indirect/"

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


def get_quarter_data(response, nodename, i, quarter_dict):
    quarters_data = response.xpath ("//tr[@nodename=$nodename]/child::td", nodename=nodename)[1:]
    try:
        text_value = quarters_data[i].xpath ('string()').extract ()[0]
    except:
        # IN RARE CASES WHERE THAT NODE DOES NOT EXIST
        text_value = "N/A"
    try:

        quarter_dict["cash flow status"][nodename] = int (text_value.replace (",", "").replace ("(", "")
                                                          .replace (")", ""))
    except:
        quarter_dict["cash flow status"][nodename] = "N/A"


NODENAMES = ['loi_nhuan_truoc_thue',
             'dieu_chinh_cac_khoan',
             'khau_hao_tai_san_co_dinh',
             'cac_khoan_du_phong',
             'loi_nhuan_thuan_dau_tu',
             'xoa_so_tai_san_co_dinh',
             'lai_lo_chenh_lech_ty_gia',
             'lai_lo_tu_thanh_ly_tai_san',
             'lai_lo_tu_hoat_dong_dau_tu',
             'lai_tien_gui',
             'thu_nhap_lai',
             'chi_phi_lai_vay',
             'cac_khoan_chi_truc_tiep',
             'loi_nhuan_tu_hoat_dong_kinh_doanh',
             'tang_giam_cac_khoan_phai_thu',
             'tang_gian_hang_ton_kho',
             'tang_giam_cac_khoan_phai_tra',
             'tang_giam_chi_phi_tra_truoc',
             'tang_giam_tai_san_ngan_han',
             'tien_lai_vay_phai_tra',
             'thue_thu_nhap_doanh_nhiep_da_nop',
             'tien_chi_tu_hoat_dong_kinh_doanh',
             'luu_chuyen_thuan_tu_hoat_dong_kinh_doanh',
             'tien_chi_mua_tai_san_co_dinh',
             'dau_tu_gop_von',
             'chi_dau_tu_ngan_han',
             'tien_chi_dau_tu_gop_von',
             'tien_thu_hoi_dau_tu_gop_von',
             'lai_tien_gui_da_thu',
             'tien_chi_mua_lai_phan_gop_von',
             'luu_chuyen_thuan_tu_hoat_dong_dau_tu',
             'tien_chi_tra_von_gop',
             'tien_chi_tra_no_thue_tai_chinh',
             'tien_chi_tra_khac_tu_hoat_dong_tai_chinh',
             'tien_chi_tra_tu_co_phan',
             'co_tu_loi_nhuan_da_tra',
             'von_gop_cac_co_dong',
             'chi_tieu_quy_phuc_loi',
             'luu_chuyen_thuan_tu_trong_ky',
             'anh_huong_thay_doi_ti_gia']


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_CF_indirect_v2"
    year_dict = {}
    direct_list = []
    errors_list = []

    def start_requests(self):
        tickers_list = extract_tickers ("tickerz.json")

        for ticker in tickers_list:
            request = scrapy.Request ('http://www.cophieu68.vn/incomestatement.php?id={0}&view=cf&year=0&lang=en'
                                      .format (ticker), callback=self.parse)
            request.meta["ticker"] = ticker
            yield request

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }

        cash_flow_type = response.xpath ("//tr[@class='tr_header']/td/text()").extract()[0]

        # EXTRACT YEAR LIST
        if cash_flow_type == "Cash Flow Direct":
            self.direct_list.append (response.meta["ticker"])
            with open ("direct_CF_list.json", "w") as direct_file:
                json.dump (self.direct_list, direct_file, indent=INDENT)
            
        else:
            quarters = response.xpath ("//tr[@class=\"tr_header\"]//td/text()").extract()[1:]
            n_quarters = len(quarters) - 1
            
            try:
                for i, quarter in enumerate(reversed(quarters)):

                    quarter_dict = {"quarter": quarter,
                                    "cash flow status": {}
                                    }

                    for nodename in NODENAMES:
                        get_quarter_data (response, nodename=nodename, i=n_quarters-i, quarter_dict=quarter_dict)

                    result["data"].append (quarter_dict)

                filename = "CF_data_{0}.json".format (result["ticker"])
                file_path = make_directory (FINANCE_PATH, filename)
                with open (file_path, 'w') as fp:
                    json.dump (result, fp, indent=INDENT)

            except:
                error_data = handle_error (response)
                self.errors_list.append(error_data)
                with open ("cophieu68_CF_indirect_errors.json", "w") as error_file:
                    json.dump (self.errors_list, error_file, indent=INDENT)
                

