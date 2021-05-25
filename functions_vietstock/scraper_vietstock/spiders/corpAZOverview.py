# This Spider gets corpAZ info on demand of the user
# Syntax:
# scrapy crawl corporateAZOnDemand

import os
import json
import scrapy
from scrapy import FormRequest, Request

import scraper_vietstock.spiders.models.constants as constants
from scraper_vietstock.spiders.models.corporateaz import *
from scraper_vietstock.helpers.fileDownloader import save_jsonfile
from scraper_vietstock.spiders.corpAZBase import corporateazBaseHandler


class corporateazOverviewHandler(corporateazBaseHandler):
    '''
    CorporateAZ Spider for getting corpAZ overview, without using Redis queue
    Instead, at the end, it exports a dict of biztype;indu and tickers within each pair
    Command line syntax: scrapy crawl corporateAZOverview
    '''

    name = name_overview
    custom_settings = settings_overview

    def __init__(self, *args, **kwargs):
        super(corporateazOverviewHandler, self).__init__(*args, **kwargs)
        
        # On-demand scrape result
        self.bizType_indu_tickers = {}

    def parse_biztype_indu_tickers(self, tickers_list, bizType_title, ind_name):
        key =  f'{bizType_title};{ind_name}'
        if key not in self.bizType_indu_tickers:
            self.bizType_indu_tickers[key] = tickers_list
        else:
            self.bizType_indu_tickers[key] += tickers_list

    def save_OnDemand_result(self, filename="localData/overview/bizType_ind_tickers_list.json"):
        save_jsonfile(self.bizType_indu_tickers, filename=filename)
