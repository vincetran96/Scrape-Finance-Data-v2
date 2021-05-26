#!/bin/bash

# kill all running workers, flush redis db, delete run files
pkill -9 -f 'celery worker'
redis-cli -h scraper-redis flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
exit 0