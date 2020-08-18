# -*- coding: utf-8 -*-

import pathlib
import random
import time

import redis
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from fad_crawl_cafef.spiders.models.constants import REDIS_HOST
from fad_crawl_cafef.spiders.models.corpaz_cafef import *
from fad_crawl_cafef.spiders.models.industriestickers_cafef import (
    industries_tickers_finished, industries_tickers_queue)


def run():
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
    indutries_id = "CafeF_ThiTruongNiemYet_Nganh"

    pages_id_elm = driver.find_element_by_id(pages_id)
    view_all_btn = pages_id_elm.find_elements_by_tag_name("a")[1]
    view_all_btn.click()
    time.sleep(5)

    ### Get all tickers on page
    ### Testing only 10 tickers
    market_content = driver.find_element_by_id(market_content_id)
    ticker_rows = market_content.find_elements_by_tag_name("tr")[1:]
    tickers_to_push = {}
    for ticker_row in ticker_rows[:1500]:
        ticker_a = ticker_row.find_elements_by_tag_name("a")[0]
        ticker_url = ticker_a.get_attribute("href")
        ticker = ticker_a.text
        print(f'Found this ticker: {ticker}')
        tickers_to_push[ticker] = ticker_url.split(ticker)[-1]

    ### Find industries
    ### Only push industries other than "Tài chính"
    r.set(industries_finished, "0")
    num_tickers = len(ticker_rows)
    industries_content = driver.find_element_by_id(indutries_id)
    industries_options = industries_content.find_elements_by_tag_name("option")
    industries_to_push = []
    for option in industries_options:
        industry_id = option.get_attribute("value")
        industry_name = option.text
        if industry_id != "341" and industry_id != "-1":
            to_push = f'{industry_id};{industry_name};{num_tickers}'
            print(f'Found this industry: {to_push}')
            industries_to_push.append(to_push)
    r.lpush(industries_queue, *industries_to_push)
    r.set(industries_finished, "1")

    ### Grab an entry pushed from industries_tickers_queue
    ### Stop grabbing if: that Spider is closed and in queue
    ### Then push to tickers queue
    switch = True
    while switch:
        it_finished = r.get(industries_tickers_finished)
        if it_finished == "1" and r.llen(industries_tickers_queue) == 0:
            switch = False
        else:
            try:
                ticker = r.lpop(industries_tickers_queue)
                print(ticker)
                if ticker in tickers_to_push.keys():
                    ticker_long_name = tickers_to_push[ticker]
                    for key in tickers_redis_keys:
                        to_push_params = f'{ticker};{ticker_long_name}'
                        r.lpush(key, to_push_params)
                        print(f'Pushed {to_push_params}')
            except Exception as e:
                print(e)
                continue

    ### Push tickers to Redis queue
    ### NOTE: to test, select 200 random tickers
    # for key in tickers_redis_keys:
        # r.lpush(key, *random.sample(tickers_to_push, 200))
        # r.lpush(key, *tickers_to_push[-100:])

    ### Close procedures
    r.set(closed_redis_key, "1")
    driver.quit()
