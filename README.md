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
        - USER_COOKIE=<specify your Vietstock cookie here without quotes>
...
```
## Build image and start related services
At the project folder, run:
```
docker-compose build --no-cache && docker-compose up
```
Next, open the scraper container within the terminal:
```
docker exec -it functions-vietstock bash
```
## From now, there are two options:
### If you want to scrape **all** tickers, financial report types, report terms:
Run `celery_run.sh` file:
```
./celery_run.sh
```
To stop the scraping, open another terminal into the scraper container and run:
```
./celery_stop.sh
```
### If you only want to scrape **one ticker, one financial report type and one report term** at a time
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

# Run Manually without Docker Compose
## Specify a local environment variables
At `functions_vietstock` folder, create a file named `.env` with the following content:
```
REDIS_HOST=localhost
PROXY=yes
TORPROXY_HOST=localhost
USER_COOKIE=<specify your Vietstock cookie here without quotes>
```
## Run Redis and Torproxy
```
docker run -d -p 6379:6379 --rm --name scraper-redis redis

docker run -it -d -p 8118:8118 -p 9050:9050 --rm --name torproxy --env TOR_NewCircuitPeriod=10 --env TOR_MaxCircuitDirtiness=60 dperson/torproxy
```
## Clear all previous running files (if any)
```
pkill -9 -f 'celery worker'
redis-cli flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
rm -v ./logs/*
rm -rf ./localData/*
rm -rf ./schemaData/*
```
Then go to the `functions_vietstock` folder:
```
cd functions_vietstock
```
## There are two options at this point, same as running with Docker Compose:
- Scrape **all** tickers, financial report types, report terms
- Scrape **one ticker, one financial report type and one report term** at a time

# Debugging and How This Thing Works
