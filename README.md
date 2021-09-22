# Scrape Financial Data of Vietnamese Listed Companies - Version 2
A standalone package to scrape financial data from listed Vietnamese companies via Vietstock. If you are looking for raw financial data from listed Vietnamese companies, this may help you.
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
Because the core components of this project runs on Docker.
## Cloning this project
Because you will have to build the image from source. I have not released this project's image on Docker Hub yet.
## A Vietstock user cookie string
How to get it:
- Sign on to [finance.vietstock.vn](https://finance.vietstock.vn/)
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
## Noting the project folder
All core functions are located within the `functions_vietstock` folder and so are the scraped files; thus, from now on, references to the `functions_vietstock` folder will be simply put as `./`.

# Run within Docker Compose (recommended) <a name="rundockercompose"></a>
## Configuration
It should be in this area:
```
...
functions-vietstock:
    build: .
        container_name: functions-vietstock
        command: wait-for-it -s scraper-redis:6379 -t 600  -- bash
        stdin_open: true
        tty: true
        environment: 
            - REDIS_HOST=scraper-redis
            - USER_COOKIE=<YOUR_VIETSTOCK_USER_COOKIE>
...
```

**July 2021 update: I have removed my own implementation of proxies for this project.** The reason will be stated in the [Lession Learned](#lessons-learned) section below. If you really want to use proxies, make your changes that can be reflected in this [constants configuration file](functions_vietstock/scraper_vietstock/spiders/models/constants.py) (more details are included there).
## Build image and start related services
At the project folder, run:
```
docker-compose build --no-cache && docker-compose up -d
```
Next, open the scraper container in another terminal:
```
docker exec -it functions-vietstock ./userinput.sh
```
## From now, you can follow along the userinput script <a name="userscript"></a>
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
    - If you enter `n`, the next prompts ask for ticker(s)
        - Again, suppose you have the `bizType_ind_tickers.csv` file
        - Then you answer the prompts as follows:
            - `ticker`: a ticker symbol or a list of ticker symbols of your choice. You can enter either `ticker_1` or `ticker_1,ticker_2`
    - Whether you chose scrape by business type-industry or tickers, you will receive a prompt for report type(s), report term(s) and page:
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

# Run on Host without Docker Compose <a name="runonhost"></a>
Maybe you do not want to spend time building the image, and just want to play around with the code.
## Install Python requirements
In your virtual environment of choice, install all requirements:
```
pip install -r requirements.txt
```
## Specify local environment variables
Nagivate to the `functions_vietstock` folder, create a file named `.env` with the following content:
```
REDIS_HOST=localhost
USER_COOKIE=<YOUR_VIETSTOCK_USER_COOKIE>
```
## Run Redis
You still need to run the Redis server inside a container:
```
docker run -d -p 6379:6379 --rm --name scraper-redis redis:6.2
```
## Clear all previous running files (if any)
Go to the `functions_vietstock` folder:
```
cd functions_vietstock
```
Run the `celery_stop.sh` script:
```
./celery_stop.sh
```
## User the userinput script to scrape
Use the `./userinput.sh` script to scrape as in the previous section.

# Scrape Results <a name="scraperesults"></a>
## CorporateAZ Overview
### File location
If you chose to scrape a list of all business types, industries and their tickers, the result is stored in the `./localData/overview` folder, under the file name `bizType_ind_tickers.csv`.
### File preview (shortened)
```
ticker,biztype_id,bizType_title,ind_id,ind_name
BID,3,Bank,1000,Finance and Insurance
CTG,3,Bank,1000,Finance and Insurance
VCB,3,Bank,1000,Finance and Insurance
TCB,3,Bank,1000,Finance and Insurance
...
```
## FinanceInfo
### File location
FinanceInfo results are stored in the `./localData/financeInfo` folder, and each file is the form `ticker_reportType_reportTermName_page.json`, representing a ticker - report type - report term - page instance.
### File preview (shortened)
```
[
    [
        {
            "ID": 4,
            "Row": 4,
            "CompanyID": 2541,
            "YearPeriod": 2017,
            "TermCode": "N",
            "TermName": "Năm",
            "TermNameEN": "Year",
            "ReportTermID": 1,
            "DisplayOrdering": 1,
            "United": "HN",
            "AuditedStatus": "KT",
            "PeriodBegin": "201701",
            "PeriodEnd": "201712",
            "TotalRow": 14,
            "BusinessType": 1,
            "ReportNote": null,
            "ReportNoteEn": null
        },
        {
            "ID": 3,
            "Row": 3,
            "CompanyID": 2541,
            "YearPeriod": 2018,
            "TermCode": "N",
            "TermName": "Năm",
            "TermNameEN": "Year",
            "ReportTermID": 1,
            "DisplayOrdering": 1,
            "United": "HN",
            "AuditedStatus": "KT",
            "PeriodBegin": "201801",
            "PeriodEnd": "201812",
            "TotalRow": 14,
            "BusinessType": 1,
            "ReportNote": null,
            "ReportNoteEn": null
        },
        {
            "ID": 2,
            "Row": 2,
            "CompanyID": 2541,
            "YearPeriod": 2019,
            "TermCode": "N",
            "TermName": "Năm",
            "TermNameEN": "Year",
            "ReportTermID": 1,
            "DisplayOrdering": 1,
            "United": "HN",
            "AuditedStatus": "KT",
            "PeriodBegin": "201901",
            "PeriodEnd": "201912",
            "TotalRow": 14,
            "BusinessType": 1,
            "ReportNote": null,
            "ReportNoteEn": null
        },
        {
            "ID": 1,
            "Row": 1,
            "CompanyID": 2541,
            "YearPeriod": 2020,
            "TermCode": "N",
            "TermName": "Năm",
            "TermNameEN": "Year",
            "ReportTermID": 1,
            "DisplayOrdering": 1,
            "United": "HN",
            "AuditedStatus": "KT",
            "PeriodBegin": "202001",
            "PeriodEnd": "202112",
            "TotalRow": 14,
            "BusinessType": 1,
            "ReportNote": null,
            "ReportNoteEn": null
        }
    ],
    {
        "Balance Sheet": [
            {
                "ID": 1,
                "ReportNormID": 2995,
                "Name": "TÀI SẢN ",
                "NameEn": "ASSETS",
                "NameMobile": "TÀI SẢN ",
                "NameMobileEn": "ASSETS",
                "CssStyle": "MaxB",
                "Padding": "Padding1",
                "ParentReportNormID": 2995,
                "ReportComponentName": "Cân đối kế toán",
                "ReportComponentNameEn": "Balance Sheet",
                "Unit": null,
                "UnitEn": null,
                "OrderType": null,
                "OrderingComponent": null,
                "RowNumber": null,
                "ReportComponentTypeID": null,
                "ChildTotal": 0,
                "Levels": 0,
                "Value1": null,
                "Value2": null,
                "Value3": null,
                "Value4": null,
                "Vl": null,
                "IsShowData": true
            },
            {
                "ID": 2,
                "ReportNormID": 3000,
                "Name": "A. TÀI SẢN NGẮN HẠN",
                "NameEn": "A. SHORT-TERM ASSETS",
                "NameMobile": "A. TÀI SẢN NGẮN HẠN",
                "NameMobileEn": "A. SHORT-TERM ASSETS",
                "CssStyle": "LargeB",
                "Padding": "Padding1",
                "ParentReportNormID": 2996,
                "ReportComponentName": "Cân đối kế toán",
                "ReportComponentNameEn": "Balance Sheet",
                "Unit": null,
                "UnitEn": null,
                "OrderType": null,
                "OrderingComponent": null,
                "RowNumber": null,
                "ReportComponentTypeID": null,
                "ChildTotal": 25,
                "Levels": 1,
                "Value1": 4496051.0,
                "Value2": 4971364.0,
                "Value3": 3989369.0,
                "Value4": 2142717.0,
                "Vl": null,
                "IsShowData": true
            },
...
```
**Please note that you have to determine whether the order of the financial values match the order of the periods**
## Logs
Logs are stored in the `./logs` folder, in the form of `scrapySpiderName_log_verbose.log`.

# Debugging and How This Thing Works <a name="debugging"></a>
## What is Redis?
"Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker." See: https://redis.io/. In this project, Redis serves as a message broker and an in-memory queue for Scrapy. No non-standard Redis configurations were made for this project.
## Debugging
### Redis
#### If scraper run in Docker container:
To open an interactive shell with Redis, you have to enter the container first:
```
docker exec -it functions-vietstock bash
```
Then:
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
## How This Scraper Works
This scraper utilizes [scrapy-redis](https://github.com/rmax/scrapy-redis) and Redis to crawl and scrape tickers' information from a top-down approach (going from business types, then industries, then tickers in each business type-industry combination) by passing necessary information into Redis queues for different Spiders to consume.
# Limitations and Lessons Learned <a name="limitations"></a>
## Limitations
- When talking about a crawler/scraper, one must consider speed, among other things. That said, I haven't run a benchmark for this scraper project.
    - There are about 3000 tickers on the market, each with its own set of available report types, report terms and pages.
    - Scraping **all** historical financials of **all** those 3000 tickers will, I believe, be pretty slow, because there are many pages for a ticker-report type-report term combination and an auto-throttle policy has been added using Scrapy's AutoThrottle extension.
    - Scrape results are written on disk, so that is also a bottleneck if you want to mass-scrape. Of course, this point is different if you only scrape one or two tickers.
    - To mass-scrape, a distributed scraping architecture is desirable, not only for speed, but also for anonymity (not entirely if you use the same user cookie across machines). However, one should respect the API service provider (i.e., Vietstock) and avoid bombarding them with tons of requests in a short period of time.
- Possibility of being banned on Vietstock? Yes.
    - Each request has a unique Vietstock user cookie on it, and thus you are identifiable when making each request.
    - As of now (May 2021), I still don't know how many concurrent requests can Vietstock server handle at any given point. While this API is publicly open, it's not documented on Vietstock. Because of this, I recently added a throttling feature to the financeInfo Spider to avoid bombarding Vietstock's server. See financeInfo's [configuration file](https://github.com/vietzerg/Scrape-Finance-Data-v2/blob/master/functions_vietstock/scraper_vietstock/spiders/models/financeinfo.py).
- Constantly changing Tor circuit maybe harmful to the Tor network.
    - Looking at [this link on Tor metrics](https://metrics.torproject.org/relayflags.html), we see that the number of exit nodes is below 2000. By changing the circuits as we scrape, we will eventually expose almost all of these available exit nodes to the Vietstock server, which in turn undermines the purpose of avoiding ban.
    - In addition, in an unlikely circumstance, interested users who want to use Tor network to view a Vietstock page may not be able to do so, because the exit node may have been banned.
- Scrape results are as-is and not processed.
    - As mentioned, scrape results are currently stored on disk as JSONs, and a unified format for financial statements has not been produced. Thus, to fully integrate this scraping process with an analysis project, you must do a lot of data standardization.
- There is no user-friendly interface to monitor Redis queue, and I haven't looked much into this.
## Lessons learned
- Utilizing Redis creates a nice and smooth workflow for mass scraping data, provided that the paths to data can be logically determined (e.g., in the form of pagination).
- Using proxies cannot offer the best anonymity while scraping, because you have to use a user cookie to have access to data anyway.
- Packing inter-dependent services with Docker Compose helps create a cleaner and more professional-looking code base.
- Why have I removed my implementation of proxies? The reason is that I believe whoever uses this software is responsible for creating and maintaining their own mechanism to avoid IP-ban. Additionally, openly pre-providing an IP-ban mechanism may expose it to being overused or even abused; and I do not want to take that risk.

# Disclaimer <a name="disclaimer"></a>
- This project is completed for educational and non-commercial purposes only.
- The scrape results are as-is from Vietstock API and without any modification. Thus, you are responsible for your own use of the data scraped using this project.
- Vietstock has all the rights to modify or remove access to the API used in this project in their own way, without any notice. I am not responsible for updating access to their API in a promptly manner and any consequences to your use of this project resulting from such mentioned change.