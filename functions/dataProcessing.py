import json
import re
import os
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch([{u'host': u'localhost', u'port': 9200}])


def toNumber(date):
    try:
        return re.findall(r'\d+', date)[0]
    except:
        return ""

# # Handle Associates data
# with open(r'associatesDetails/AAA_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data:
#         temps = i["Details"]
#         for temp in temps:
#             # Process date data
#             temp["ClosedDate"] = toNumber(temp["ClosedDate"])
#             temp["AssociatesDate"] = toNumber(temp["AssociatesDate"])
#             temp["LastUpdate"] = toNumber(temp["LastUpdate"])
#         output[toNumber(i["ClosedDate"])] = temps
#     print(output)

# # Handle BoardDetails data
# with open(r'boardDetails/AGM_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data:
#         temps = i["Details"]
#         for temp in temps:
#             # Process data
#             temp["Position"] = toNumber(temp["Position"])
#             if temp["YearOfBirth"] == -1:
#                 temp["YearOfBirth"] = None

#             temp["FromDate"] = toNumber(temp["FromDate"])
#             if temp["FromDate"] == "":
#                 temp["FromDate"] = None

#             temp["TimeSticking"] = toNumber(temp["TimeSticking"])
#             if temp["TimeSticking"] == "":
#                 temp["TimeSticking"] = None

#         output[toNumber(i["ClosedDate"])] = temps

# # Handle Counterparts data
# with open(r'counterparts/A32_counterparts.json') as f:
#     data = json.load(f)
#     output = []
#     for i in data:
#         temp = {}
#         temp["StockCode"] = i["StockCode"]
#         temp["CatID"] = i["CatID"]
#         temp["MarketCapital"] = i["MarketCapital"]
#         temp["PE"] = i["PE"]
#         temp["PB"] = i["PB"]
#         output.append(temp)
#     print(output)

# # Handle Company info data
# with open(r'ctkhDetails/AAM_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     output["CompanyID"] = data[1][0]["CompanyID"]
#     output["IndustryID"] = data[1][0]["IndustryID"]
#     output["SubIndustry"] = data[1][0]["SubIndustry"]
#     output["CatID"] = data[1][0]["CatID"]

# Handle FinanceInfo:CTKH


def getKey(data):
    temp = str(data["YearPeriod"])
    if not str(data["PeriodBegin"]) == "None":
        temp += str(data["PeriodBegin"])
    if not str(data["PeriodEnd"]) == "None":
        temp += str(data["PeriodEnd"])
    return (temp, str(data["ID"]))

# with open(r'financeInfo/A32_CTKH_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for i in data[1]:
#         for item in output.items():
#             item[1][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:BCTT
# with open(r'financeInfo/AAA_BCTT_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for key in data[1].keys():
#         for k in output.keys():
#             output[k][key] = {}
#         for i in data[1][key]:
#             for item in output.items():
#                 item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:CDKT
# with open(r'financeInfo/AAA_CDKT_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for key in data[1].keys():
#         for k in output.keys():
#             output[k][key] = {}
#         for i in data[1][key]:
#             for item in output.items():
#                 item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:CSTC
# with open(r'financeInfo/AAA_CSTC_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for key in data[1].keys():
#         for k in output.keys():
#             output[k][key] = {}
#         for i in data[1][key]:
#             for item in output.items():
#                 item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:CTKH
# with open(r'financeInfo/AAA_CTKH_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for i in data[1]:
#         for item in output.items():
#             item[1][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:KQKD
# with open(r'financeInfo/AAA_KQKD_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for key in data[1].keys():
#         for k in output.keys():
#             output[k][key] = {}
#         for i in data[1][key]:
#             for item in output.items():
#                 item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle FinanceInfo:LC
# with open(r'financeInfo/AAA_LC_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data[0]:
#         output[getKey(i)[0]] = {"ID" : getKey(i)[1]}
#     for key in data[1].keys():
#         for k in output.keys():
#             output[k][key] = {}
#         for i in data[1][key]:
#             for item in output.items():
#                 item[1][key][i["NameEn"]] = i["Value"+item[1]["ID"]]
#     print(output)

# # Handle majorShareHolder data
# with open(r'majorShareholders/ACL_Page_1.json') as f:
#     data = json.load(f)
#     output = {}
#     for i in data:
#         temps = i["Details"]
#         for temp in temps:
#             # Process data
#             temp["ShareholderDate"] = toNumber(temp["ShareholderDate"])
#         output[toNumber(i["ShareholderDate"])] = temps
#     print(output)


def genData(_doc: {}):
    yield {
        "_index": "test1",
        "_id": "AAA",
        "_source": {
            "cid": "AAA",
            "data": [{k: v for k, v in _doc.items()}]
        }
    }


def genDataUpd(_doc: {}):
    yield {
        "_index": "test1",
        "_id": "AAA",
        '_op_type': 'update',
        "script": {
                    "inline": "ctx._source.data.add(params.tag)",
                    "lang": "painless",
                    "params": {
                        "tag": {k: v for k, v in _doc.items()}
                    }

        }
    }


# Handle ownerStructure data
with open(r'ownerStructure/AAA_Page_1.json') as f:
    data = json.load(f)
    output = []
    for i in data:
        temp_ = {}
        temps = i["Details"]
        for temp in temps:
            # Process data
            temp["ClosedDate"] = toNumber(temp["ClosedDate"])
        temp_["timestamp"] = toNumber(i["ClosedDate"])
        temp_["ownerStructure"] = temps
        output.append(temp_)
    # print(output)
    # helpers.bulk(es, genData(output[0]))
    try:
        helpers.bulk(es, genDataUpd(output[1]))
    except elasticsearch.helpers.errors.BulkIndexError:
        helpers.bulk(es, genData(output[1]))
