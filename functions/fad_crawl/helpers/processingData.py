import re

def toNumber(date):
    try:
        return re.findall(r'\d+', date)[0]
    except:
        return ""

def getKey(data):
    temp = str(data["YearPeriod"])
    if not str(data["PeriodBegin"]) == "None":
        temp += str(data["PeriodBegin"])
    if not str(data["PeriodEnd"]) == "None":
        temp += str(data["PeriodEnd"])
    return (temp, str(data["ID"]))