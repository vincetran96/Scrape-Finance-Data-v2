from celery import group

from celery_tasks import *
from fad_crawl.spiders.financeInfo import financeInfoHandler
from fad_crawl.spiders.getProxy import getProxyHanlder
from fad_crawl.spiders.main import corporateazHandler
from fad_crawl.spiders.pdfDocs import pdfDocsHandler

if __name__ == '__main__':
    # g = group(multiplier.signature((2,3), immutable=True), subtractor.signature((4,5), immutable=True))
    # adder.apply_async((10,20),link=g)
    
    crawler_group = group(crawl_spider_corpAZ.signature(immutable=True),
                            crawl_spider_finInfo.signature(immutable=True))
    
    crawl_spider_getProxy.apply_async(link=crawler_group)
