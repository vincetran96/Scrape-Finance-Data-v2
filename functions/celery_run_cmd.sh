#!/bin/bash

# clear old files and potentially running workers
pkill -9 -f 'celery worker'
redis-cli flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
rm -v ./logs/*
rm -rf ./localData/*
rm -rf ./schemaData/*

# create workers
celery -A celery_main worker -Q corpAZ -c 10 -n workercorpAZ@%h -l INFO --detach --pidfile="./run/celery/%n.pid"
celery -A celery_main worker -Q finance -c 10 -n workerfinance@%h -l INFO --detach  --pidfile="./run/celery/%n.pid"
celery -A celery_main worker -Q es -c 10 -n workeres@%h -l INFO -f logs/workeres.log --detach  --pidfile="./run/celery/%n.pid"

# constantly check if workers are online; if yes run tasks
while true; do
    status=$(celery -A celery_main status | grep '3 nodes')
    if [ "$status" == "3 nodes online." ]; then
        echo "=== running celery tasks ==="
        python celery_run_tasks.py
        break
    else
        echo "=== waiting for workers to be online ==="
    fi
done

# constantly check if scrapy has finished
SCRAPY_RUN_DIR=./run/scrapy/
while true; do
    sleep 5
    if [ "$(ls -A $SCRAPY_RUN_DIR)" ]; then
        echo "=== scrapy is still running ==="
    else
        echo "=== scrapy has finished ==="
        break
    fi
done
