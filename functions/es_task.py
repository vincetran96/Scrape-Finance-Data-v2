from celery_main import app

# Elastic client module
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from fad_crawl.helpers.esGenData import *
from fad_crawl.helpers.processingData import *

@app.task
def handleES_task(index, id, resp_json = ""):
    print("=== UPDATING ES DATABASE ===")
    es = Elasticsearch([{u'host': u'localhost', u'port': 9200}])
    output = []

    # Handle owenerStructure data
    if index == "ownerstructure":
        for i in resp_json:
            temp_ = {}
            temps = i["Details"]
            for temp in temps:
                # Process data
                temp["ClosedDate"] = toNumber(temp["ClosedDate"])
            temp_["timestamp"] = toNumber(i["ClosedDate"])
            temp_["ownerStructure"] = [{str(k).replace(" ", "").lower() : v for k, v in _.items()} for _ in temps]
            output.append(temp_)
    
    # Handle majorShareholders data
    elif index == "majorshareholders":
        for i in data:
            temp_ = {}
            temps = i["Details"]
            for temp in temps:
                # Process data
                temp["ShareholderDate"] = toNumber(temp["ShareholderDate"])
            temp_["timestamp"] = toNumber(i["ShareholderDate"])
            temp_["Shareholder"] = [{str(k).replace(" ", "").lower() : v for k, v in _.items()} for _ in temps]
            output.append(temp_)

    #Pushing data to ES Database
    for docs in output:
        try:
            helpers.bulk(es, genDataUpd(index,id, docs))
        except:
            helpers.bulk(es, genData(index,id, docs))  