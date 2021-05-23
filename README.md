# Scrape Financial Data of Vietnamese Listed Companies - Version 2

As this repo is under heavy re-development, documentation is minimal at the moment.

# Prerequisites
## A computer that can run Docker
Obviously.
## A Vietstock user cookie string
How to get it:
- Sign on to finance.vietstock.vn
- Hover over **"Corporate"**/**"Doanh nghiệp"**, and choose **"Corporate A-Z"**/**"Doanh nghiệp A-Z"**
- Click on any ticker
- Open your browser's Inspect console by right-clicking on any empty area of the page, and choose `Inspect`
- Go to the `Network` tab, filter only `XHR` requests
- On the page, click **"Financials"**/**"Tài chính"**
- On the list of `XHR` requests, click on any requests, then go to the `Cookies` tab underneath
- Take note of the the string in the `vts_usr_lg` cookie, which is your user cookie
- Done
## Some pointers about Vietstock financial API parameters, which will be used when scraping
### Financial report types and their meanings:

Report type code | Meaning
--- | ---
`CTKH` | Financial targets/**C**hỉ **T**iêu **K**ế **H**oạch
`CDKT` | Balance sheet/**C**ân **Đ**ối **K**ế **T**oán
`KQKD` | Income statement/**K**ết **Q**uả **K**inh **D**oanh
`LC` | Cash flow statement/**L**ưu **C**huyển (Tiền Tệ)
`CSTC` | Financial ratios/**C**hỉ **S**ố **T**ài **C**hính

### Financial report terms and their meanings:

Report term code | Meaning
--- | ---
`1` | Annually
`2` | Quarterly


# Run within Docker Compose (recommended)
## Add your Vietstock user cookie to `docker-compose.yml`
It should be in this area:
```
...
functions-vietstock:
    build: .
    container_name: functions-vietstock
    command: wait-for-it -s torproxy:8118 -s scraper-redis:6379 -t 600  -- bash
    environment: 
        - REDIS_HOST=scraper-redis
        - PROXY=yes
        - TORPROXY_HOST=torproxy
        - USER_COOKIE=<your Vietstock cookie without quotes>
...
```
## Build image and start related services
At the project folder, run:
```
docker-compose build --no-cache && docker-compose up
```
Next, open the scraper container in another terminal:
```
docker exec -it functions-vietstock bash
```
## From now, there are two options:
### 1. If you want to scrape **all** tickers, financial report types, report terms:
Run `celery_run.sh` file:
```
./celery_run.sh
```
To stop the scraping, open another terminal into the scraper container and run:
```
./celery_stop.sh
```
### 2. If you only want to scrape **one ticker, one financial report type and one report term** at a time
- First, you may want to get the list of all listed tickers and their respective business types and industries. Run the following command:
    ```
    scrapy crawl corporateAZOnDemand
    ```
- Next, you will find a file named `bizType_ind_tickers_list.json`, which contains all listed ticker symbols under their respective business types and industries (in the dict keys of the form `business_type;industry`)
- After choosing your interested ticker(s), run the following command to scrape financial reports:
    ```
    scrapy crawl financeInfoOnDemand -a ticker=<ticker symbol> -a report_type=<report type code> -a report_term=<report term code> -a page=<page number>
    ```
    - Explanation of arguments:
        - `ticker`: a ticker symbol of your choice
        - `report_type` and `report_term`: see the following tables (which was already mentioned above)
            Report type code | Meaning
            --- | ---
            `CTKH` | Financial targets/**C**hỉ **T**iêu **K**ế **H**oạch
            `CDKT` | Balance sheet/**C**ân **Đ**ối **K**ế **T**oán
            `KQKD` | Income statement/**K**ết **Q**uả **K**inh **D**oanh
            `LC` | Cash flow statement/**L**ưu **C**huyển (Tiền Tệ)
            `CSTC` | Financial ratios/**C**hỉ **S**ố **T**ài **C**hính


            Report term code | Meaning
            --- | ---
            `1` | Annually
            `2` | Quarterly
        - `page`: the page number for the scrape, this is optional. If omitted, the scraper will start from page 1

# Run on Host without Docker Compose because Why Not
## Specify local environment variables
At `functions_vietstock` folder, create a file named `.env` with the following content:
```
REDIS_HOST=localhost
PROXY=yes
TORPROXY_HOST=localhost
USER_COOKIE=<your Vietstock cookie without quotes>
```
## Run Redis and Torproxy
You still need to run these inside containers:
```
docker run -d -p 6379:6379 --rm --name scraper-redis redis

docker run -it -d -p 8118:8118 -p 9050:9050 --rm --name torproxy --env TOR_NewCircuitPeriod=10 --env TOR_MaxCircuitDirtiness=60 dperson/torproxy
```
## Clear all previous running files (if any)
Go to the `functions_vietstock` folder:
```
cd functions_vietstock
```
Run the following commands in the terminal:
```
pkill -9 -f 'celery worker'
docker exec scraper-redis redis-cli flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
rm -v ./logs/*
rm -rf ./localData/*
rm -rf ./schemaData/*
```
## There are two options at this point, same as running with Docker Compose:
- Scrape **all** tickers, financial report types, report terms
- Scrape **one ticker, one financial report type and one report term** at a time

# Scrape Results
Results are stored in the `localData` folder.

Logs are stored in the `logs` folder.

More details coming.

# Debugging and How This Thing Works
## What is Torproxy and Why is it Required?
### Quick introduction
Torproxy is "Tor and Privoxy (web proxy configured to route through tor) docker container." See: https://github.com/dperson/torproxy. We need it in this container to avoid IP-banning for scraping too much, I suppose.
### What else should I know about it?
The only two configuration variables I used with Torproxy are `TOR_MaxCircuitDirtiness` and `TOR_NewCircuitPeriod`, which means the maximum Tor circuit age (in seconds) and time period between every attempt to change Tor circuit (in seconds), respectively. Note that `TOR_MaxCircuitDirtiness` is set at max = 60 seconds, and `TOR_NewCircuitPeriod` is set at 10 seconds.
## What is Redis and Why is it Required?
"Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker." See: https://redis.io/. In this project, Redis serves as a message broker and an in-memory queue for Scrapy.
## Debugging
### Redis
#### If scraper run in Docker container:
To open an interactive shell with Redis:
```
redis-cli -h scraper-redis
```
#### If scraper run on host:
To open an interactive shell with Redis:
```
docker exec scraper-redis redis-cli
```
### Celery
I don't know what to write here for now.

# Limitations and Lessons Learned
## Limitations
- When talking about a crawler/scraper, one must consider speed, among other things. That said, I haven't run a benchmark for this scraper project.
    - Last time I checked, there are about 3000 tickers on the market.
    - Scraping **all** historical financials of **all** 3000 tickers will, I believe, be pretty slow, because we have to use Torproxy and there can be many pages for a ticker-report type-report term combination.
    - Scrape results are written on disk, so that is also a bottleneck if you want to mass-scrape. Of course, this point is different if you only scrape one or two tickers.
    - To mass-scrape, a distributed scraping architecture is desirable, not only for speed, but also for anonymity.
- Possibility of being banned on Vietstock? Yes.
    - Each request has a unique Vietstock user cookie on it, and thus you are identifiable when making each request.
    - As of now (May 2021), I still don't know how many concurrent requests can Vietstock server take at any given point. While this API is open publicly, it's not documented on Vietstock.
## Lessons learned
A lot.
