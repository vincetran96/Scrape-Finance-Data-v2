# Scrape Financial Data of Vietnamese Listed Companies - Version 2

# Table of Contents
- [Prerequisites](#prerequisites)
- [Run within Docker Compose](#rundockercompose)
- [Run on Host](#runonhost)
- [Scrape Results](#scraperesults)
- [Debugging and How It Works](#debugging)
- [Limitations and Lessons Learned](#limitations)
- [Disclaimer](#disclaimer)

# Prerequisites <a name="prerequisites"></a>
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


# Run within Docker Compose (recommended) <a name="rundockercompose"></a>
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
        - USER_COOKIE=<YOUR_VIETSTOCK_USER_COOKIE>
...
```
## Build image and start related services
At the project folder, run:
```
docker-compose build --no-cache && docker-compose up -d
```
Next, open the scraper container in another terminal:
```
docker exec -it functions-vietstock ./userinput.sh
```
## From now, you can follow along the userinput script
Note: To stop the scraping, stop the userinput script terminal, then open another terminal and run:
```
docker exec -it functions-vietstock ./celery_stop.sh
```
to clean everything related to the scraping process (local scraped files are intact).

**Some quesitons require you to answer in a specific syntax, as follows:**
- `Do you wish to scrape by a specific business type-industry or by tickers? [y for business type-industry/n for tickers] `
    - If you enter `y`, the next prompt is: `Enter business type ID and industry ID combination in the form of businesstype_id;industry_id: `
        - If you chose to scrape a list of all business types-industries and their respective tickers, you should have the file `bizType_ind_tickers.csv` in the scrape result folder (`./localData/overview`).
        - Then you answer this prompt by entering a business type ID and industry ID combination in the form of `businesstype_id;industry_id`.
    - If you enter `n`, the next prompts ask for ticker(s), report type(s), report term(s) and page.
        - Again, suppose you have the `bizType_ind_tickers.csv` file
        - Then you answer the prompts as follows:
            - `ticker`: a ticker symbol or a list of ticker symbols of your choice. You can enter either `ticker_1` or `ticker_1,ticker_2`
            - `report_type` and `report_term`: use the report type codes and report term codes in the following tables (which was already mentioned above). You can enter either `report_type_1` or `report_type_1,report_type_2`. Same goes for report term.
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

# Run on Host without Docker Compose because Why Not <a name="runonhost"></a>
## Specify local environment variables
At `functions_vietstock` folder, create a file named `.env` with the following content:
```
REDIS_HOST=localhost
PROXY=yes
TORPROXY_HOST=localhost
USER_COOKIE=<YOUR_VIETSTOCK_USER_COOKIE>
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
```
## User the userinput script to scrape
Use the `./userinput.sh` script to scrape as in the previous section.

# Scrape Results <a name="scraperesults"></a>
## CorporateAZ Overview
If you chose to scrape a list of all business types, industries and their tickers, the result is stored in the `./localData/overview` folder, under the file name `bizType_ind_tickers.csv`.

## FinanceInfo
FinanceInfo results are stored in the `./localData/financeInfo` folder, and each file is the form `ticker_reportType_reportTermName_page.json`, representing a ticker - report type - report term - page instance.

## Logs
Logs are stored in the `./logs` folder, in the form of `scrapySpiderName_log_verbose.log`.

# Debugging and How This Thing Works <a name="debugging"></a>
## What is Torproxy?
### Quick introduction
Torproxy is "Tor and Privoxy (web proxy configured to route through tor) docker container." See: https://github.com/dperson/torproxy. We need it in this container to avoid IP-banning for scraping too much.
### Configuration used in this project
The only two configuration variables I used with Torproxy are `TOR_MaxCircuitDirtiness` and `TOR_NewCircuitPeriod`, which means the maximum Tor circuit age (in seconds) and time period between every attempt to change Tor circuit (in seconds), respectively. Note that `TOR_MaxCircuitDirtiness` is set at max = 60 seconds, and `TOR_NewCircuitPeriod` is set at 10 seconds.
## What is Redis?
"Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker." See: https://redis.io/. In this project, Redis serves as a message broker and an in-memory queue for Scrapy. No non-standard Redis configurations were made for this project.
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
docker exec -it scraper-redis redis-cli
```
### Celery
Look inside each log file.

# Limitations and Lessons Learned <a name="limitations"></a>
## Limitations
- When talking about a crawler/scraper, one must consider speed, among other things. That said, I haven't run a benchmark for this scraper project.
    - There are about 3000 tickers on the market, each with its own set of available report types, report terms and pages.
    - Scraping **all** historical financials of **all** those 3000 tickers will, I believe, be pretty slow, because we have to use Torproxy and there can be many pages for a ticker-report type-report term combination.
    - Scrape results are written on disk, so that is also a bottleneck if you want to mass-scrape. Of course, this point is different if you only scrape one or two tickers.
    - To mass-scrape, a distributed scraping architecture is desirable, not only for speed, but also for anonymity (not entirely if you use the same user cookie across machines). However, one should respect the API service provider (i.e., Vietstock) and avoid bombarding them with tons of requests in a short period of time.
- Possibility of being banned on Vietstock? Yes.
    - Each request has a unique Vietstock user cookie on it, and thus you are identifiable when making each request.
    - As of now (May 2021), I still don't know how many concurrent requests can Vietstock server handle at any given point. While this API is publicly open, it's not documented on Vietstock.
- Scrape results data format.
    - As mentioend, scrape results are currently stored on disk as JSONs, and a unified format for financial statements has not been produced. Thus, to fully integrate this scraping process with an analysis project, you must do a lot of data standardization.
## Lessons learned
- Utilizing Redis creates a nice and smooth workflow for mass scraping data, provided that the paths to data can be logically determined (e.g., in the form of pagination).
- Using proxies cannot offer the best anonymity while scraping, because you have to use a user cookie to have access to data anyway.
- Packing inter-dependent services with Docker Compose helps create a cleaner and more professional-looking code base.

# Disclaimer <a name="disclaimer"></a>
- This project is completed for educational and non-commercial purposes only.
- The scrape results are as-is from Vietstock API and without any modification. Thus, you are responsible for your own use of the data scraped using this project.
- Vietstock has all the rights to modify or remove access to the API used in this project in their own way, without any notice. I am not responsible for updating access to their API in a promptly manner and any consequences to your use of this project resulting from such mentioned change.