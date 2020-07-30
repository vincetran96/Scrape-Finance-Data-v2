# -*- coding: utf-8 -*-

from fad_crawl_cafef.spiders.models.bs_cafef import name as bs_name
from fad_crawl_cafef.spiders.models.is_cafef import name as is_name
from fad_crawl_cafef.spiders.models.cf_d_cafef import name as cf_d_name
from fad_crawl_cafef.spiders.models.cf_ind_cafef import name as cf_ind_name


tickers_redis_keys = [
                      f'{bs_name}:tickers',
                      f'{is_name}:tickers',
                      f'{cf_d_name}:tickers',
                      f'{cf_ind_name}:tickers'
                    ]
