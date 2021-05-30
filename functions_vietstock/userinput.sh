#!/bin/bash

while true; do
    echo "Scrape Finance Data - version 2"
    echo
    while true; do
        read -p "Do you wish to mass scrape? [y/n] " massyn
        if [[ "$massyn" == "y" || "$massyn" == "Y" ]]; then
            while true; do
                read -p "Do you wish clear ALL scraped files and kill ALL running Celery workers? [y/n] " yn
                if [[ "$yn" == "y" || "$yn" == "Y" ]]; then
                    echo "Clearing scraped files and all running workers, please wait..."
                    output="$(pkill -9 -f 'celery worker')"
                    echo $output
                    output1="$(redis-cli -h scraper-redis flushall)"
                    echo $output1
                    output2="$(rm -v ./run/celery/*) $(rm -v ./run/scrapy/*) $(rm -v ./logs/*) $(rm -rf ./localData/*)"
                    echo $output2
                    break
                elif [[ "$yn" == "n" || "$yn" == "N" ]]; then
                    echo "You chose not to clear scraped files and all running workers"
                    break
                else    
                    echo "Please provide your answer."
                fi
            done
            while true; do
                read -p "Do you wish to start mass scraping now? Process will automatically exit when finished. [y] " startmassy
                if [[ "$startmassy" == "y" || "$startmassy" == "Y" ]]; then
                    echo "Creating Celery workers..."
                    celery -A celery_main worker -Q corpAZ -c 10 -n workercorpAZ@%h -l INFO --detach --pidfile="./run/celery/%n.pid"
                    celery -A celery_main worker -Q finance -c 10 -n workerfinance@%h -l INFO --detach  --pidfile="./run/celery/%n.pid"

                    while true; do
                        status=$(celery -A celery_main status | grep '2 nodes')
                        if [ "$status" == "2 nodes online." ]; then
                            echo "Running Celery tasks for mass scrape..."
                            python celery_run_tasks.py
                            break
                        else
                            echo "Waiting for Celery workers to be online..."
                        fi
                    done

                    SCRAPY_RUN_DIR=./run/scrapy/
                    while true; do
                        sleep 10
                        if [ "$(ls -A $SCRAPY_RUN_DIR)" ]; then
                            echo "Scrapy is still running..."
                        else
                            echo "Scrapy has finished"
                            break
                        fi
                    done

                    echo "Killing Celery workers, flushing Redis queues, deleting Celery run files..."
                    pkill -9 -f 'celery worker'
                    redis-cli -h scraper-redis flushall
                    rm -v ./run/celery/*
                    echo "Exiting..."
                    exit 0
                else
                    echo "Hang on then."
                fi
            done
        elif [[ "$massyn" == "n" || "$massyn" == "N" ]]; then
            read -p "Do you wish to scrape a list of all business types-industries and their respective tickers? This may help you choose your interested tickers to scrape. [y/n] " corpazoverviewyn
            if [[ "$corpazoverviewyn" == "y" || "$corpazoverviewyn" == "Y" ]]; then
                echo "Running corpAZ Overview Spider..."
                scrapy crawl corporateAZOverview
                echo "List of business types, industries and their tickers was saved at localData/overview/bizType_ind_tickers.csv"
            elif [[ "$corpazoverviewyn" == "n" || "$corpazoverviewyn" == "N" ]]; then
                echo "You declined to run corpAZ Overview Spider."
            else
                echo "Choose!"
            fi
            while true; do
                read -p "Do you wish to scrape by a specific business type-industry or by tickers? [y for business type-industry/n for tickers] " bityn
                if [[ "$bityn" == "y" || "$bityn" == "Y" ]]; then
                    read -p "Enter business type ID and industry ID combination in the form of businesstype_id;industry_id: " biz_ind_ids
                    read -p "Enter report type id(s): " report_type
                    read -p "Enter report term id(s): " report_term
                    echo "=== Start scraping $biz_ind_ids, report type(s) $report_type, report term(s) $report_term ... See log file(s) for more details."
                    python clean_queue.py
                    scrapy crawl corporateAZExpress -a biz_ind_ids=$biz_ind_ids & PIDCORPAZ=$!
                    scrapy crawl financeInfo -a report_type=$report_type -a report_term=$report_term & PIDFININFO=$!
                    wait $PIDCORPAZ
                    wait $PIDFININFO
                    echo "=== Exiting..."
                    exit 0
                elif [[ "$bityn" == "n" || "$bityn" == "N" ]]; then
                    read -p "Enter a ticker, or a tickers list in the form of ticker1,ticker2,...: " ticker
                    read -p "Enter report type id(s): " report_type
                    read -p "Enter report term id(s): " report_term
                    read -p "Enter starting page number (if empty, default to 1): " page
                    if [[ "$page" == "" ]]; then
                        echo "Page number defaulted to 1"
                        echo "=== Start scraping $ticker, report type(s) $report_type, report term(s) $report_term, starting from page 1 ... See log file(s) for more details."
                        scrapy crawl financeInfo -a ticker=$ticker -a report_type=$report_type -a report_term=$report_term -a page=1
                        echo "=== Exiting..."
                        exit 0
                    elif ! [[ "$page" =~ ^[0-9]+$ ]]; then
                        echo "Please enter a positive integer only."
                    else
                        echo "=== Start scraping $ticker, report type(s) $report_type, report term(s) $report_term, starting from page $page ... See log file(s) for more details."
                        scrapy crawl financeInfo -a ticker=$ticker -a report_type=$report_type -a report_term=$report_term -a page=$page
                        echo "=== Exiting..."
                        exit 0
                    fi
                else
                    echo "Please provide your answer."
                fi        
            done
        else
            echo "Please provide your answer."
        fi
    done
done
