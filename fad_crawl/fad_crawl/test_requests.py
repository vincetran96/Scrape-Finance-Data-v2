# For scrapy shell
from scrapy import FormRequest

# tickers list
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
                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
                         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                     },
                     cookies={
                         "language": "vi-VN",
                         "vts_usr_lg": "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBEDE986E6558A3C0BA"
                     })

# balance sheet
req_bs = FormRequest(url="https://finance.vietstock.vn/data/financeinfo",
                     formdata={
                         "Code": "AAA",
                         "ReportType": "CDKT",
                         "ReportTermType": "2",
                         "Unit": "1000000",
                         "Page": "1",
                         "PageSize": "4"
                     },
                     headers={
                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
                         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                     },
                     cookies={
                         "language": "vi-VN",
                         "vts_usr_lg": "DAA88872CB57C5F7D9A1BEAC17FA8EB45B13EC22ED84130BEB211A74526AA2FF08DDC77E8C8A64AE831BB94133CA74318498D44C0DE5D53A0E70864683D96869205D0BB94F2D6244D660A25F294BA4E24EAA4268C3066F534C095CFA8E3D194F42C981F1B8A87FBEDE986E6558A3C0BA"
                     })
