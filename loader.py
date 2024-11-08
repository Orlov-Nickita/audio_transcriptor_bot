import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

OPEN_AI_LOGIN = os.getenv('OPEN_AI_LOGIN')
OPEN_AI_PASS = os.getenv('OPEN_AI_PASS')

REDIS_USER = os.getenv('REDIS_USER')
REDIS_PASS = os.getenv('REDIS_PASS')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_DB = os.getenv('REDIS_DB')

ADMINISTRATORS = {
    "Никита": os.environ["ADMINISTRATOR_NIKITA"],
    "Саша": os.environ["ADMINISTRATOR_SASHA"],
    "Паша": os.environ["ADMINISTRATOR_PASHA"],
}

redis_url = f'redis://{REDIS_USER}:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
