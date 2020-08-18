import re
import datetime


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
    """Simplify string by removing non-alphanumeric characters
    and apply lowercase
    """
    import re
    s1 = s.split(".")[-1]
    s1 = re.sub(r"\W+", " ", s1)
    s1 = " ".join(s1.split())
    s1 = s1.lower()
    s1 = s1.strip()
    return s1


def rmvEmpStr(l):
    """Remove empty string from list
    """
    return [e for e in l if e != ""]


def removeDigit(s):
    """Remove all digits from string
    """
    pattern = '[0-9]'
    s = re.sub(pattern, '', s)
    return s
