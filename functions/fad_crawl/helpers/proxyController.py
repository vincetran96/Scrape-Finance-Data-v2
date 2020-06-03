import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller


def get_proxies():
    parser = BeautifulSoup(requests.get('https://free-proxy-list.net/', headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}).text, 'html.parser')
    proxies = []
    for row in parser.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        print (cols)
        cols = [ele.text.strip() for ele in cols]
        if cols[-2] == "yes":
            proxies.append(cols[0] + ':' + cols[1])
    return proxies

def checkAndAddProxyPool():
    proxies = get_proxies()
    url = 'https://httpbin.org/ip'
    okayProxyPool = []
# TODO: Improve concurrency here... too slow    
    for proxy in proxies:
        try:
            response = requests.get(url, proxies={"https": proxy})
            if response.status_code == 200:
                okayProxyPool.append(proxy)
        except:
            pass
    return okayProxyPool

def changeTorIP(password=None):
    if password != None:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=password)
            controller.signal(Signal.NEWNYM)


if __name__ == '__main__':
    print ("GETTING PROXIES...")
    print (checkAndAddProxyPool())
    print ("DONE")
    