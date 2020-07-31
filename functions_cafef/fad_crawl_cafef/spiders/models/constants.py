import os
from dotenv import load_dotenv


load_dotenv(os.path.join("", ".env"))

USER_AGENT = ""
CONTENT_TYPE = ""
USER_COOKIE = ""

redis_host = os.getenv('REDIS_HOST')
REDIS_HOST = redis_host

REPORT_TERMS = {"0":"Annual", "4":"Quarter"}
CURRENT_YEAR = 2020
BACKWARDS_YEAR = 2015

ERROR_SET_SUFFIX = "error_set_cafef"
