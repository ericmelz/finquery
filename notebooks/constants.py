import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_LLM_MODEL = os.getenv('OPENAI_LLM_MODEL')
