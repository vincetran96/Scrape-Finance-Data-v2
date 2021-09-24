import scraper_vietstock.spiders.models.utilities as utilities


name = "testSpider"

log_settings = utilities.log_settings(
    spiderName=name,
    log_level="INFO",
    log_formatter="scraper_vietstock.spiders.models.utilities.TickerSpiderLogFormatter"
)
