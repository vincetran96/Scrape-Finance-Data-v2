from celery import Celery
from fad_crawl.spiders.main import crawl_test
from fad_crawl.spiders.main import crawl_main

# use Redis for broker/backend

app = Celery('tasks', broker='pyamqp://zerg:1234@localhost/zerg_vhost',
             backend='rpc://')

# @app.task
def crawl_task():
    crawl_main()
    # crawl_test()

# @app.task
def crawl_task1():
    crawl_test()
