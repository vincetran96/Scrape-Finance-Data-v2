# -*- coding: utf-8 -*-
import fad_crawl_cafef.spiders.models.constants as constants
import fad_crawl_cafef.spiders.models.utilities as utilities
from fad_crawl_cafef.spiders.models.corpaz_cafef import industries_queue
from fad_crawl_cafef.spiders.models.corpaz_cafef import industries_finished


name = "IndustriesTickers_cafef"
industries_tickers_finished = f'{name}:finished'
industries_tickers_queue = f'{name}:tickers'


indtickers = {"url": "https://solieu6.mediacdn.vn/ProxyHandler.ashx?RequestName=CompanyInfo&RequestType=json&TradeId=-2&IndustryId={0}&Keyword=&PageIndex=1&PageSize={1}&Type=0",
        "headers": {
            "User-Agent": constants.USER_AGENT,
            "Referer": "https://s.cafef.vn/du-lieu-doanh-nghiep.chn"
        },
        "cookies": {
        },
        "meta": {
            "industry_id": "",
            "industry_name": "",
        }}

log_settings = utilities.log_settings(spiderName=name,
                                      log_level="INFO",
                                      log_formatter=None
                                      )

redis_key_settings = {"REDIS_START_URLS_KEY": industries_queue}

concurrency_settings = {'CONCURRENT_REQUESTS': 100}

settings = {**log_settings, **redis_key_settings, **concurrency_settings}
