import datetime
import json

import elasticsearch
from elasticsearch import Elasticsearch, helpers

from celery_main import app
from fad_crawl.helpers.esGenData import *
from fad_crawl.helpers.processingData import *
from fad_crawl.spiders.models.constants import ELASTICSEARCH_HOST


### Initiate ES
es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': 9200}])


### ES indices for fin statements
FIN_STATEMENTS_INDICES = {
    'LC': 'cashflow',
    'KQKD': 'incomestatement',
    'CDKT': 'balancesheets'
}

### Load mapping tables
with open("functions/schema/lookup_dict_all_nonfin.json", "r") as jsonfile:
    LOOKUP_DICT=json.load(jsonfile)
    jsonfile.close()
with open("functions/schema/mapping_dict_all_nonfin.json", "r") as jsonfile:
    MAPPING_DICT=json.load(jsonfile)
    jsonfile.close()


### Create ES task
@app.task
def handleES_task(index, id, resp_json = "", finInfoType = ""):
    print("=== UPDATING {} {}: {} DATABASE ===".format(index,finInfoType,id))
    output = []
    controlES = True
    mapping = mappingDict(index)

    ##! This part for data preprocessing 
    # Handle owenerStructure data
    if index == "ownerstructure":
        for i in resp_json:
            return_ = []
            for j in i["Details"]:
                return_.append({mapping[str(k).replace(".", "").lower()]: j[k] 
                                for k in j.keys() 
                                if str(k).replace(".", "").lower() in mapping})
            output.append({
                "timestamp" : toNumber(i["ClosedDate"]),
                index : return_
            })

    # Handle majorShareholders data
    elif index == "majorshareholders":
        for i in resp_json:
            return_ = []
            for j in i["Details"]:
                return_.append({mapping[str(k).replace(".", "").lower()]: j[k] 
                                for k in j.keys() 
                                if str(k).replace(".", "").lower() in mapping})
            output.append({
                "timestamp" : toNumber(i["ShareholderDate"]),
                index : return_
            })

    # Handle ctkhDetails data: Company info data
    #! There is a case of Vietstock doesnt store this data, the query return two empty list.
    elif index == "ctkhdetails":
        try:
            helpers.bulk(es, genData(index,
                                     id, 
                                     {mapping[k]: resp_json[1][0][k] for k in mapping.keys()}
                                     )) 
        except IndexError:
            print("WARNING: No CompanyInfo data (ctkhDetails) on {}".format(id))
        controlES = False

    # Handle Counterparts data
    elif index == "counterparts":
        for i in resp_json:
            output.append({mapping[k]: i[k] for k in mapping.keys()})

    # Handle BoardDetails, associatesdetails data
    elif index == "boarddetails" or index == "associatesdetails":
        for i in resp_json:
            return_ = []
            for j in i["Details"]:
                _ = {mapping[k]: j[k] 
                    for k in j.keys() 
                    if k in mapping}
                if all(i==None for i in _.values()) : continue
                if index == "boarddetails":
                    _["fromdate"] = toNumber(_["fromdate"])
                    if _["fromdate"] == "": _["fromdate"] = -1 
                return_.append(_)
            end = int(toNumber(i["ClosedDate"]))
            if len(return_) != 0:
                output.append({
                    "timestamp" : 
                        {
                            "startdate": int(datetime.datetime(int(datetime.datetime.fromtimestamp(end/1000).strftime('%Y')), 1, 1).timestamp() * 1000),
                            "enddate": end
                        },
                    index : return_
                })

    # Handle FinanceInfo:LC, FinanceInfo:KQKD, FinanceInfo:CDKT data
    # DONE
    elif index == "financeinfo" and finInfoType in FIN_STATEMENTS_INDICES.keys():
        # Getting data from json return
        output = {}
        for period in resp_json[0]:
            period_name = getPeriodName(period)
            period_key, period_id = getKey(period)
            output[period_key] = {"ID" : period_id, "Period": period_name}
        for report_fullname in resp_json[1].keys():
            for k in output.keys():
                output[k][report_fullname] = {}
            for acc_content in resp_json[1][report_fullname]:
                try:
                    acc_n = get_fad_acc(finInfoType, report_fullname, acc_content, LOOKUP_DICT, MAPPING_DICT)
                except:
                    acc_n = simplifyText(acc_content['Name']) + ";nonFAD"
                for item in output.items():
                    item[1][report_fullname][acc_n] = acc_content["Value"+item[1]["ID"]]

        # Processing data to ES friendly format
        output = processFinanceInfo(output,id)
        index = FIN_STATEMENTS_INDICES[finInfoType]

    # Handle FinanceInfo:CTKH data
    # DONE
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
                # Handle when the key is empty
                try:
                    if item[1][""] == None:
                        del item[1][""]
                    else:
                        print("ERROR: There is a None Key with non-null value at {} when updating {}.".format(id,"financialplan"))
                        continue
                except:
                    pass
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
    # DONE
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
        # Processing data to ES friendly format
        output_ = []
        for item in output.items():
            start, end = getDate(item[0])
            del item[1]["ID"]
            # Checking if all data is null then skip
            _ = True
            for i in item[1].values():
                for j in i.values():
                    if j != None:
                        _ = False
                        break
            if not _:
                # Handle when the key is empty
                for i in item[1].keys():
                    item[1][i] = {str(k).replace(".", "").lower() : v for k, v in item[1][i].items()}
                    try:
                        if item[1][""] == None:
                            del item[1][""]
                        else:
                            print("ERROR: There is a None Key with non-null value at {} when updating {}.".format(id,"financialratios"))
                            _ = True
                            break
                    except:
                        pass
                if not _:
                    # Generate the ES output
                    output_.append({"timestamp": 
                                        {
                                            "startdate": start,
                                            "enddate": end
                                        },
                                    "reporttype" : "financialratios",
                                    "data": item[1],
                                    }
                                    )
            else:
                continue
        output = output_
        index = "financialratios"

    #! This part for controlling ES push method.
    if controlES:
        #Pushing data to ES Database: "counterpart"
        if index == "counterparts":
            for docs in output:
                try:
                    helpers.bulk(es, genDataUpdNoTimestamp(index,id, docs))
                except elasticsearch.helpers.errors.BulkIndexError:
                    helpers.bulk(es, genData(index,id, docs))  
        #Pushing data to ES Database
        else:
            for docs in output:
                try:
                    helpers.bulk(es, genDataUpd(index,id, docs))
                except elasticsearch.helpers.errors.BulkIndexError:
                    helpers.bulk(es, genData(index,id, docs))           
