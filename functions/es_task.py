from celery_main import app

# Elastic client module
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from fad_crawl.helpers.esGenData import *
from fad_crawl.helpers.processingData import *

@app.task
def handleES_task(index, id, resp_json = "", finInfoType = ""):
    print("=== UPDATING ES DATABASE ===")
    es = Elasticsearch([{u'host': u'localhost', u'port': 9200}])
    output = []
    controlES = True

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
        for i in resp_json:
            temp_ = {}
            temps = i["Details"]
            for temp in temps:
                # Process data
                temp["ShareholderDate"] = toNumber(temp["ShareholderDate"])
            temp_["timestamp"] = toNumber(i["ShareholderDate"])
            temp_["Shareholder"] = [{str(k).replace(" ", "").lower() : v for k, v in _.items()} for _ in temps]
            output.append(temp_)

    # Handle FinanceInfo:LC data
    elif index == "financeinfo" and finInfoType == "LC":
        # Getting data from json return
        output = {}
        for i in resp_json[0]:
            output[getKey(i)[0]] = {"ID": getKey(i)[1]}
        for key in resp_json[1].keys():
            for k in output.keys():
                output[k][key] = {}
            for i in resp_json[1][key]:
                for item in output.items():
                    item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]

        # Processing data to ES friendly format
        output = processFinanceInfo(output)
        index = "cashflow"

    # Handle FinanceInfo:KQKD data
    elif index == "financeinfo" and finInfoType == "KQKD":
        # Getting data from json return
        output = {}
        for i in resp_json[0]:
            output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
        for key in resp_json[1].keys():
            for k in output.keys():
                output[k][key] = {}
            for i in resp_json[1][key]:
                for item in output.items():
                    item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]

        # Processing data to ES friendly format
        output = processFinanceInfo(output)
        index = "incomestatement"

    # Handle FinanceInfo:CTKH data
    elif index == "financeinfo" and finInfoType == "CTKH":
        output = {}
        for i in resp_json[0]:
            output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
        for i in resp_json[1]:
            for item in output.items():
                item[1][i["NameEn"]] = i["Value"+item[1]["ID"]]
        
        # Processing data to ES friendly format
        output_ = []
        for item in output.items():
            start, end = getDate(item[0])
            del item[1]["ID"]
            # Checking if all data is null then skip
            _ = True
            for i in item[1].values():
                if i != None:
                    _ = False
                    break
            if not _:
                # Generate the ES output
                output_.append({"timestamp": 
                                    {
                                        "startdate": start,
                                        "enddate": end
                                    },
                                "reporttype" : "financialplan",
                                "data": item[1],
                                }
                                )
            else:
                continue
        output = output_
        index = "financialplan"

    # Handle FinanceInfo:CSTC data
    elif index == "financeinfo" and finInfoType == "CSTC":
        output = {}
        for i in resp_json[0]:
            output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
        for key in resp_json[1].keys():
            for k in output.keys():
                output[k][key] = {}
            for i in resp_json[1][key]:
                for item in output.items():
                    item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
        print(output)
        # Processing data to ES friendly format
        output_ = []
        for item in output.items():
            start, end = getDate(item[0])
            del item[1]["ID"]
            # Checking if all data is null then skip
            _ = True
            for i in item[1].values():
                if i != None:
                    _ = False
                    break
            if not _:
                # Generate the ES output
                output_.append({"timestamp": 
                                    {
                                        "startdate": start,
                                        "enddate": end
                                    },
                                "reporttype" : "ratios",
                                "data": item[1],
                                }
                                )
            else:
                continue
        output = output_
        index = "financialratios"

    # Handle FinanceInfo:CDKT data
    elif index == "financeinfo" and finInfoType == "CDKT":
        output = {}
        for i in resp_json[0]:
            output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
        for key in resp_json[1].keys():
            for k in output.keys():
                output[k][key] = {}
            for i in resp_json[1][key]:
                for item in output.items():
                    item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
        # print(output)
        # Processing data to ES friendly format
        output = processFinanceInfo(output)
        print(output)
        index = "balancesheets"

    # Handle ctkhDetails data
    elif index == "ctkhdetails":
        output = {}
        output["CompanyID"] = resp_json[1][0]["CompanyID"]
        output["IndustryID"] = resp_json[1][0]["IndustryID"]
        output["SubIndustry"] = resp_json[1][0]["SubIndustry"]
        output["CatID"] = resp_json[1][0]["CatID"]
        helpers.bulk(es, genData(index,id, output)) 
        controlES = False
    
    # Handle Counterparts data
    elif index == "ctkhdetails":
        output = []
        for i in resp_json:
            temp = {}
            temp["StockCode"] = i["StockCode"]
            temp["CatID"] = i["CatID"]
            temp["MarketCapital"] = i["MarketCapital"]
            temp["PE"] = i["PE"]
            temp["PB"] = i["PB"]
            output.append(temp)
        

    if controlES:
        #Pushing data to ES Database
        for docs in output:
            try:
                helpers.bulk(es, genDataUpd(index,id, docs))
            except elasticsearch.helpers.errors.BulkIndexError:
                helpers.bulk(es, genData(index,id, docs))  