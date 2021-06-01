# This module contains queue cleaning procedures for the main app

import redis
from scraper_vietstock.spiders.models.constants import REDIS_HOST


def clean_redis_queue():
    r = redis.Redis(host=REDIS_HOST)
    r.flushdb()

if __name__ == "__main__":
    clean_redis_queue()
