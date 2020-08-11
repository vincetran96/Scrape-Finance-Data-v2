import datetime
import re
import traceback


def toNumber(date):
    try:
        return int(re.findall(r'\d+', date)[0])
    except:
        return ""


def getKey(data):
    temp = str(data["YearPeriod"])
    if not str(data["PeriodBegin"]) == "None":
        temp += str(data["PeriodBegin"])
    if not str(data["PeriodEnd"]) == "None":
        temp += str(data["PeriodEnd"])
    return (temp, str(data["ID"]))


def getPeriodName(data):
    try:
        return data['TermNameEN'] + "-" + str(data['YearPeriod'])
    except:
        return "N/A-N/A"


def daysdict(year):
    if (((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0)):
        return {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    return {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def getDate(chr):
    if len(chr) == 4:
        start = int(datetime.datetime(int(chr[:5]), 1, 1).timestamp() * 1000)
        end = int(datetime.datetime(int(chr[:5]), 12, 31).timestamp() * 1000)
    else:
        dtc = daysdict(int(chr[:5]))
        start = int(datetime.datetime(int(chr[4:8]),
                                      int(chr[8:10]),
                                      1).timestamp() * 1000)
        end = int(datetime.datetime(int(chr[-6:-2]),
                                    int(chr[-2:]),
                                    dtc[int(chr[-2:])]).timestamp() * 1000)
    return start, end


def simplifyText(s):
    s1 = s.split(".")[-1]
    s1 = re.sub(r"\W+", " ", s1)
    s1 = " ".join(s1.split())
    s1 = s1.lower()
    return s1


def get_fad_acc(report, report_fullname, d, lookup_dict, mapping_dict):
    """Returns the final FAD account name based on the report type and 
    a dict which is an account of a report in the financeInfo API
    Params:
        `report`: financeInfo report type: ['LC', 'KQKD', 'CDKT']
        `report_fullname`: Cashflow Indirect, ...
        `d`: account dictionary of JSON response from API
        `lookup_dict`: from lookup_dict_all in `schema` folder
        `mapping_dict`: from mapping_dict_all in `schema` folder
        `
    """
    acc_n = simplifyText(d['NameEn'])
    acc_vi_n = simplifyText(d['Name'])
    parent_n = simplifyText(lookup_dict[report][report_fullname][str(d['ParentReportNormID'])]['NameEn'])
    parent_vi_n = simplifyText(lookup_dict[report][report_fullname][str(d['ParentReportNormID'])]['Name'])
    try:
        return mapping_dict[report][report_fullname][f'{acc_n};{parent_n};{acc_vi_n};{parent_vi_n}']
    except:
        print(traceback.format_exc())
        return "N/A"


def processFinanceInfo(output, _id=""):
    output_ = []
    for item in output.items():
        print(item)
        start, end = getDate(item[0])
        # Getting the cashflow type
        for key in item[1].keys():
            if key != "ID":
                reporttype = key
                break

        # Checking if all data is null then skip
        _ = True
        for i in item[1][reporttype].values():
            if i != None:
                _ = False
                break
        if not _:
            # Handle when the key is empty
            item[1][reporttype] = {str(k).replace(
                ".", "").lower(): v for k, v in item[1][reporttype].items()}
            try:
                if item[1][reporttype][""] == None:
                    del item[1][reporttype][""]
                else:
                    print(
                        "ERROR: There is a None Key with non-null value at {} when updating {}.".format(_id, reporttype))
                    continue
            except:
                pass

            # Generate the ES output
            output_.append({"timestamp":
                            {
                                "startdate": start,
                                "enddate": end
                            },
                            "reporttype": reporttype,
                            "data": item[1][reporttype],
                            }
                           )
        else:
            continue
    return output_


def mappingDict(index):
    if index == "ownerstructure":
        return {
            "shareholderen": "shareholdergroup",
            "companyid": "companyid",
            "shares": "shares",
            "rate": "sharespercentage"
        }
    elif index == "majorshareholders":
        return {
            "shareholdernamevn" : "namevn",
            "shareholdernameen" : "nameen",
            "quantity" : "shares",
            "ratio": "sharespercentage"
        }
    elif index == "ctkhdetails":
        return {
            "CompanyID" : "companyid",
            "IndustryID" : "industryid",
            "SubIndustry" : "subindustry",
            "CatID": "catid"
        }  
    elif index == "counterparts":
        return {
            "StockCode" : "companycode",
            "CatID" : "catid",
            "MarketCapital" : "marketcap",
            "PE": "pe",
            "PB": "pb",
        }  
    elif index == "boarddetails":
        return {
            "CompanyID" : "companyid",
            "Name" : "name",
            "YearOfBirth" : "yearofbirth",
            "PersonalShares": "personalshares",
            "NationalShares": "nationalshares",
            "TotalShares": "totalshares",
            "FromDate": "fromdate",
            "TitleText": "title",
            "GradeText": "education",
            "PositionText": "position"
        } 
    elif index == "associatesdetails":
        return {
            "CompanyID" : "companyid",
            "Associates" : "nameen",
            "Associates_VN" : "namevn",
            "CharteredCapital": "capital",
            "OwnerRatio": "ownerratio",
            "AssociateTypeID": "associatetypeid",
            "Industry": "industry",
            "ContributeValue": "contributevalue"
        }
    else:
        return {}
