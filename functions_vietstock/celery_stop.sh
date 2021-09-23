#!/bin/bash

# kill all running workers, flush redis db, delete run files
pkill -9 -f 'celery worker'
pkill -9 -f 'celery_main'
redis-cli -h scraper-redis flushall || docker exec scraper-redis redis-cli flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
exit 0