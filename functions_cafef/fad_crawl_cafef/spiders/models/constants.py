import os
from dotenv import load_dotenv


load_dotenv(os.path.join("", ".env"))

redis_host = os.getenv('REDIS_HOST')
REDIS_HOST = redis_host
