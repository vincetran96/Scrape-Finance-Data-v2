from celery_tasks import adder, crawl_task


if __name__ == '__main__':
    result = crawl_task.delay()
    print ('Task finished? '), result.ready()
    