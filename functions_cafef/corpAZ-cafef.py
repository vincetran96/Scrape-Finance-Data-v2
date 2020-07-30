import pathlib
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import redis
from fad_crawl_cafef.spiders.models.constants import REDIS_HOST


r = redis.Redis(host=REDIS_HOST, decode_responses=True)

CAFEF_DOMAIN = "s.cafef.vn"
BALANCE_SHEET_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/BSheet/2019/4/1/1/bao-cao-tai-chinh-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
BS_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/BSheet/{1}/4/1/1/bao-cao-tai-chinh{2}"

INCOME_STATEMENT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/IncSta/2019/4/1/1/ket-qua-hoat-dong-kinh-doanh-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
IS_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/IncSta/{1}/4/1/1/ket-qua-hoat-dong-kinh-doanh{2}"

CF_INDIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlow/2019/4/1/1/luu-chuyen-tien-te-gian-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
CF_IND_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlow/{1}/4/1/1/luu-chuyen-tien-te-gian-tiep{2}"

CF_DIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlowDirect/2019/4/1/1/luu-chuyen-tien-te-truc-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
CF_D_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlowDirect/{1}/4/1/1/luu-chuyen-tien-te-truc-tiep{2}"


current_path = pathlib.Path(__file__).parent.absolute()
chromedriver_location = f'{current_path}/execs/chromedriver'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=chromedriver_location,chrome_options=chrome_options)
driver.get("https://s.cafef.vn/du-lieu-doanh-nghiep.chn")

pages_id = "CafeF_ThiTruongNiemYet_Trang"
pages_id_elm = driver.find_element_by_id(pages_id)
view_all_btn = pages_id_elm.find_elements_by_tag_name("a")[1]
view_all_btn.click()
time.sleep(5)

market_content_id = "CafeF_ThiTruongNiemYet_Content"
market_content = driver.find_element_by_id(market_content_id)
ticker_rows = market_content.find_elements_by_tag_name("tr")[1:]
for ticker_row in ticker_rows:
    ticker_a = ticker_row.find_elements_by_tag_name("a")[0]
    ticker_url = ticker_a.get_attribute("href")
    ticker = ticker_a.text
    print(ticker, ticker_url.split(ticker)[-1])

r.lpush()

driver.quit()
