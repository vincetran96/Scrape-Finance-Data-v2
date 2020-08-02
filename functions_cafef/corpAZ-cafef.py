# -*- coding: utf-8 -*-

import pathlib
import time
import random

import redis
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from fad_crawl_cafef.spiders.models.constants import REDIS_HOST
from fad_crawl_cafef.spiders.models.corpaz_cafef import (closed_redis_key,
                                                         tickers_redis_keys)


CAFEF_DOMAIN = "s.cafef.vn"

INCOME_STATEMENT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/IncSta/2019/4/1/1/ket-qua-hoat-dong-kinh-doanh-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
IS_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/IncSta/{1}/{2}/1/1/ket-qua-hoat-dong-kinh-doanh{3}"

CF_INDIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlow/2019/4/1/1/luu-chuyen-tien-te-gian-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
CF_IND_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlow/{1}/{2}/1/1/luu-chuyen-tien-te-gian-tiep{3}"

CF_DIRECT_URL = "https://s.cafef.vn/bao-cao-tai-chinh/VSI/CashFlowDirect/2019/4/1/1/luu-chuyen-tien-te-truc-tiep-cong-ty-co-phan-dau-tu-va-xay-dung-cap-thoat-nuoc.chn"
CF_D_URL = "https://s.cafef.vn/bao-cao-tai-chinh/{0}/CashFlowDirect/{1}/{2}/1/1/luu-chuyen-tien-te-truc-tiep{3}"


### Setup Redis
r = redis.Redis(host=REDIS_HOST, decode_responses=True)
r.set(closed_redis_key, "0")

### Setup Chromium
current_path = pathlib.Path(__file__).parent.absolute()
chromedriver_location = f'{current_path}/execs/chromedriver'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=chromedriver_location,chrome_options=chrome_options)
driver.get("https://s.cafef.vn/du-lieu-doanh-nghiep.chn")

### CafeF elements
pages_id = "CafeF_ThiTruongNiemYet_Trang"
market_content_id = "CafeF_ThiTruongNiemYet_Content"

pages_id_elm = driver.find_element_by_id(pages_id)
view_all_btn = pages_id_elm.find_elements_by_tag_name("a")[1]
view_all_btn.click()
time.sleep(5)

### Get all tickers on page
market_content = driver.find_element_by_id(market_content_id)
ticker_rows = market_content.find_elements_by_tag_name("tr")[1:]
tickers_to_push = []
for ticker_row in ticker_rows:
    ticker_a = ticker_row.find_elements_by_tag_name("a")[0]
    ticker_url = ticker_a.get_attribute("href")
    ticker = ticker_a.text
    to_push = ticker + ";" + ticker_url.split(ticker)[-1]
    print(f'Found this ticker: {to_push}')
    tickers_to_push.append(to_push)

### Push tickers to Redis queue
### NOTE: to test, select 100 random tickers
for key in tickers_redis_keys:
    r.lpush(key, *random.sample(tickers_to_push, 200))
    # r.lpush(key, *tickers_to_push[-100:])

### Close procedures
r.set(closed_redis_key, "1")
driver.quit()
