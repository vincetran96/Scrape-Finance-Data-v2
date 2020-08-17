import os
from dotenv import load_dotenv


load_dotenv(os.path.join("", ".env"))

USER_AGENT = ""
CONTENT_TYPE = ""
USER_COOKIE = ""

redis_host = os.getenv('REDIS_HOST')
REDIS_HOST = redis_host

REPORT_TERMS = {"0":"Annual", "4":"Quarter"}
CURRENT_YEAR = 2020
BACKWARDS_YEAR = 2015

ERROR_SET_SUFFIX = "error_set_cafef"


### OLD CONSTANTS
# CAFEF_DOMAIN = "s.cafef.vn"

# INCOME_STATEMENT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/IncSta/2019/4/1/1/ket-qua-hoat-dong-kinh-doanh-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
# IS_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/IncSta/{1}/{2}/1/1/ket-qua-hoat-dong-kinh-doanh{3}"

# CF_INDIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlow/2019/4/1/1/luu-chuyen-tien-te-gian-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
# CF_IND_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlow/{1}/{2}/1/1/luu-chuyen-tien-te-gian-tiep{3}"

# CF_DIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlowDirect/2019/4/1/1/luu-chuyen-tien-te-truc-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
# CF_D_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlowDirect/{1}/{2}/1/1/luu-chuyen-tien-te-truc-tiep{3}"
