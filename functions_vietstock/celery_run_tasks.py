
# This module runs task imported from celery_tasks

from celery import group
from celery_tasks import *


if __name__ == '__main__':    
    prerun_cleanup_task.delay()
    corporateAZExpress_task.delay()
    finance_task.delay()
    # corporateAZ_task.delay()
    # associates_task.delay()
    # finance_task.delay()
    # counterparts_task.delay()
    # majorshareholders_task.delay()
    # ownerstructure_task.delay()
    # ctkhdetails_task.delay()
    # boarddetails_task.delay()
    # viewprofile_task.delay()
