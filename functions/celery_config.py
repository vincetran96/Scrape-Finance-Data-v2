# -*- coding: utf-8 -*-
# This module contains settings for Celery

from fad_crawl.spiders.models.constants import REDIS_HOST



# Broker settings.
broker_url = f'redis://{REDIS_HOST}:6379'

# List of modules to import when the Celery worker starts.
include = ['celery_tasks']

# Using the database to store task state and results.
result_backend = f'redis://{REDIS_HOST}:6379'

# Routing
task_routes = {
    'celery_tasks.prerun_cleanup_task': {'queue': 'corpAZ'},
    'celery_tasks.corporateAZ_task': {'queue': 'corpAZ'},
    'celery_tasks.pdfDocs_task': {'queue': 'corpAZ'},
    'celery_tasks.associates_task': {'queue': 'corpAZ'},
    'celery_tasks.counterparts_task': {'queue': 'corpAZ'},
    'celery_tasks.majorshareholders_task': {'queue': 'corpAZ'},
    'celery_tasks.ownerstructure_task': {'queue': 'corpAZ'},
    'celery_tasks.ctkhdetails_task': {'queue': 'corpAZ'},
    'celery_tasks.boarddetails_task': {'queue': 'corpAZ'},
    'celery_tasks.finance_task': {'queue': 'finance'}
}
