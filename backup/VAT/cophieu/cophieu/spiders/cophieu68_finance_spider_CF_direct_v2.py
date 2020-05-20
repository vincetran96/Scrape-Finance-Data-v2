import scrapy
import sys
import json
import traceback
import os

INDENT = 2

FINANCE_PATH = "cash_flow_statements/direct/"


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


NODENAMES = ['tien_thu_tu_ban_hang',
             'tien_chi_tra_cho_nguoi_cung_cap',
             'tien_chi_tra_cho_nguoi_lao_dong',
             'tien_chi_tra_lai_vay',
             'tien_chi_nop_thue_thu_nhap_doanh_nghiep',
             'tien_chi_nop_thue_gia_tri_gia_tang',
             'tien_thu_khac_tu_hoat_dong_king_doanh',
             'tien_chi_khac_cho_hoat_dong_king_doanh',
             'luu_chuyen_tien_thuan_thu_hoat_dong_king_doanh',
             'tien_chi_de_mua_sam',
             'tien_thu_tu_thanh_ly',
             'tien_chi_cho_vay',
             'tien_thu_hoi_cho_vay',
             'tien_chi_dau_tu_gop_vop_vao_don_vi_khac',
             'tien_thu_hoi_dau_tu_gop_von_vao_don_vi_khac',
             'tien_thu_lai_cho_vay',
             'luu_chuyen_tien_thuan_tu_hoat_dong_dau_tu',
             'tien_thu_tu_phat_hanh_co_phieu',
             'tien_chi_tra_von_gop_cho_cac_chu_so_huu',
             'tien_vay_ngan_han',
             'tien_chi_tra_no_goc_vay',
             'tien_chi_de_mua_sam_xay_dung',
             'tien_chi_tra_thue_tai_chinh',
             'co_tuc_loi_nhuan',
             'chi_tu_cac_quy_doanh_nghiep',
             'luu_chuyen_tien_thuan_tu_hoat_dong_tai_chinh',
             'luu_chuyen_tien_thuan_trong_ky',
             'tien_va_tuong_duong_tien_dau_ky',
             'anh_huong_cua_thay_doi_ty_gia',
             'tien_va_tuong_duong_cuoi_ky']


class FinanceSpider (scrapy.Spider):
    name = "cophieu68_finance_CF_direct_v2"
    year_dict = {}
    errors_list = []

    def start_requests(self):
        with open ("direct_CF_list.json", encoding="utf-8") as jsonfile:
            text = json.load (jsonfile)
            for i, ticker in enumerate(text):
                request = scrapy.Request ("http://www.cophieu68.vn/incomestatement.php?id={0}&view=cf&year=0%lang=vn"
                                          .format (ticker), callback=self.parse)
                request.meta["ticker"] = ticker
                request.meta['count'] = i
                yield request

    def parse(self, response):
        result = {
            "ticker": response.meta["ticker"],
            "data": []
        }
        quarters = response.xpath ("//tr[@class='tr_header']//td/text()").extract ()[1:]
        n_quarters = len(quarters) - 1

        try:
            for i, quarter in enumerate (reversed(quarters)):

                quarter_dict = {"quarter": quarter,
                                "cash flow status": {},
                                }

                for nodename in NODENAMES:
                    get_quarter_data (response, nodename=nodename, i=n_quarters-i, quarter_dict=quarter_dict)

                result["data"].append(quarter_dict)

            filename = "CF_data_{0}.json".format (result["ticker"])
            file_path = make_directory (FINANCE_PATH, filename)
            with open (file_path, 'w') as fp:
                json.dump (result, fp, indent=INDENT)

        except:
            error_data = handle_error (response)
            self.errors_list.append(error_data)
            with open ("cophieu68_CF_indirect_errors.json", "w") as error_file:
                json.dump (self.errors_list, error_file, indent=INDENT)
