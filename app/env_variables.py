# Import required modules
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

TRINO_HOST = os.getenv('TRINO_HOST')
TRINO_PORT = os.getenv('TRINO_PORT')
TRINO_USER = os.getenv('TRINO_USER')
TRINO_PASS = os.getenv('TRINO_PASS')

LOGGING_NAME = os.getenv('LOGGING_NAME')

X_API_KEY = os.getenv('X_API_KEY')
IS_VIRTUAL_HOST = os.getenv('IS_VIRTUAL_HOST')
IS_VIRTUAL_PORT = os.getenv('IS_VIRTUAL_PORT')

SAP_USERNAME = os.getenv('SAP_USERNAME')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')
SAP_CLIENT = os.getenv('SAP_CLIENT', '100')
SAP_LANGUAGE = os.getenv('SAP_LANGUAGE', 'EN')
SAP_AUTH_URL = os.getenv('SAP_AUTH_URL')
SAP_BASE_URL = os.getenv('SAP_BASE_URL')
