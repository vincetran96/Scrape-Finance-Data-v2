from celery import Celery
from functions.fad_crawl.spiders.main import crawl_test
from functions.fad_crawl.spiders.main import crawl_main

app = Celery('tasks', broker='pyamqp://zerg:1234@localhost/zerg_vhost',
             backend='rpc://')

@app.task
def crawl_task():
    # crawl_main()
    crawl_test()