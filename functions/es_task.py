from celery_main import app

# Elastic client module
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from fad_crawl.helpers.esGenData import *

@app.task
def handleES_task(index, id, docs = ""):
    print("=== UPDATING ES DATABASE ===")
    es = Elasticsearch([{u'host': u'localhost', u'port': 9200}])
    try:
        helpers.bulk(es, genDataUpd(index,id, docs))
    except:
        helpers.bulk(es, genData(index,id, docs))  