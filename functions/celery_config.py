# -*- coding: utf-8 -*-
# This module contains settings for Celery

# Broker settings.
broker_url = 'redis://localhost:6379'

# List of modules to import when the Celery worker starts.
include = ['celery_tasks']

# Using the database to store task state and results.
result_backend = 'redis://localhost:6379'

# Routing
task_routes = {
    'celery_tasks.prerun_cleanup_task': {'queue': 'corpAZ'},
    'celery_tasks.corporateAZ_task': {'queue': 'corpAZ'},
    'celery_tasks.pdfDocs_task': {'queue': 'corpAZ'},
    'celery_tasks.finance_task': {'queue': 'finance'},
    'celery_tasks.associates_task': {'queue': 'corpAZ'},
    'celery_tasks.counterparts_task': {'queue': 'corpAZ'},
}
