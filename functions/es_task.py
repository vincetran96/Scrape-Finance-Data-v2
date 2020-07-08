from celery_main import app
import datetime
# Elastic client module
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from fad_crawl.helpers.esGenData import *
from fad_crawl.helpers.processingData import *
from fad_crawl.spiders.models.constants import ELASTICSEARCH_HOST

es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': 9200}])


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
        
    # Handle FinanceInfo:LC data
    # DONE
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
        output = processFinanceInfo(output,id)
        index = "cashflow"

    # Handle FinanceInfo:KQKD data
    # DONE
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
        output = processFinanceInfo(output,id)
        index = "incomestatement"

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

    # Handle FinanceInfo:CDKT data
    # DONE
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
        # Processing data to ES friendly format
        output = processFinanceInfo(output)
        index = "balancesheets"


    # Handle BoardDetails data
    # DONE
    elif index == "boarddetails":
        data = resp_json
        output = {}
        for i in data:
            temps = i["Details"]
            for temp in temps:
                try:
                    del temp["IDNO"]
                    del temp["ClosedDate"]
                    del temp["CompanyID"]
                    del temp["Title"]
                    del temp["Position"]
                    del temp["Grade"]
                except:
                    pass
                # Process data
                if temp["YearOfBirth"] == -1:
                    temp["YearOfBirth"] = None

                temp["FromDate"] = toNumber(temp["FromDate"])
                if temp["FromDate"] == "":
                    temp["FromDate"] = None

                temp["TimeSticking"] = toNumber(temp["TimeSticking"])
                if temp["TimeSticking"] == "":
                    temp["TimeSticking"] = None

            output[toNumber(i["ClosedDate"])] = temps
        
        # Processing data to ES friendly format
        output_ = []
        for item in output.items():
            end = int(item[0])
            start = int(datetime.datetime(int(datetime.datetime.fromtimestamp(end/1000).strftime('%Y')), 1, 1).timestamp() * 1000)
            # Checking if all data is null then skip
            _ = True
            for i in item[1]:
                for j in i.values():
                    if j != None:
                        _ = False
                        break
            if not _:
                # Handle when the key is empty
                for i in range(0,len(item[1])):
                    item[1][i] = {str(k).replace(".", "").lower() : v for k, v in item[1][i].items()}
                    try:
                        if item[1][i][""] == None:
                            del item[1][i][""]
                        else:
                            print("ERROR: There is a None Key with non-null value at {} when updating {}.".format(id,"boarddetails"))
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
                                    "reporttype" : "boarddetails",
                                    "data": item[1],
                                    }
                                    )
            else:
                continue
        output = output_

    # Handle Associates data
    elif index == "associatesdetails":
        data = resp_json
        output = {}
        for i in data:
            temps = i["Details"]
            for temp in temps:
                try:
                    del temp["ClosedDate"]
                    del temp["AssociatesDate"]
                    del temp["Associates_VN"]
                    del temp["hc_IDNO"]
                except:
                    pass            
                # Process date data
                
                temp["LastUpdate"] = toNumber(temp["LastUpdate"])
                temp["CurrencyUnit"] = str(temp["CurrencyUnit"]).replace(" ", "")
            output[toNumber(i["ClosedDate"])] = temps
        # print(output)
        # Processing data to ES friendly format
        output_ = []
        for item in output.items():
            end = int(item[0])
            start = int(datetime.datetime(int(datetime.datetime.fromtimestamp(end/1000).strftime('%Y')), 1, 1).timestamp() * 1000)
            # Checking if all data is null then skip
            _ = True
            for i in item[1]:
                for j in i.values():
                    if j != None:
                        _ = False
                        break
            if not _:
                # Handle when the key is empty
                for i in range(0,len(item[1])):
                    item[1][i] = {str(k).replace(".", "").lower() : v for k, v in item[1][i].items()}
                    try:
                        if item[1][i][""] == None:
                            del item[1][i][""]
                        else:
                            print("ERROR: There is a None Key with non-null value at {} when updating {}.".format(id,"boarddetails"))
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
                                    "reporttype" : "associates",
                                    "data": item[1],
                                    }
                                    )
            else:
                continue
        output = output_

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

