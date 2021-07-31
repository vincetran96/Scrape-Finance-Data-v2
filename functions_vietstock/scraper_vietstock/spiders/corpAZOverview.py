# This Spider gets corpAZ info on demand of the user


from scraper_vietstock.spiders.models.corporateaz import *
from scraper_vietstock.helpers.fileDownloader import save_csvfile_row, save_csvfile_rows_add
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
        
        # Initialize on-demand scrape result
        save_csvfile_row(("ticker","biztype_id", "bizType_title", "ind_id", "ind_name"), overview_csv_name)

    def overview_biztype_indu_tickers(self, tickers_list, bizType_id, bizType_title, ind_id, ind_name):
        rows = (
            (ticker, bizType_id, bizType_title, ind_id, ind_name)
            for ticker in tickers_list
        )
        save_csvfile_rows_add(rows, filename=overview_csv_name)
