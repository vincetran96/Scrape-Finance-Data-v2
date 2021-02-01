# -*- coding: utf-8 -*-
# This module runs task imported from celery_tasks

from celery import group
from celery_tasks import *

if __name__ == '__main__':
    
    # prerun_cleanup_task.apply_async(link=g) 
    prerun_cleanup_task.delay()
    corporateAZ_cafef_task.delay()
    industriestickers_cafef_task.delay()
    balancesheet_cafef_task.delay()
