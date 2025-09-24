# Import required modules
import os
from dotenv import load_dotenv

# Load Environment variables from .env file
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '')

TRINO_HOST = os.getenv('TRINO_HOST', 'localhost')
TRINO_PORT = os.getenv('TRINO_PORT', '8080')
TRINO_USER = os.getenv('TRINO_USER', 'admin')
TRINO_PASS = os.getenv('TRINO_PASS', '')

LOGGING_NAME = os.getenv('LOGGING_NAME', 'odata-middleware')

X_API_KEY = os.getenv('X_API_KEY', 'productapikey')
IS_VIRTUAL_HOST = os.getenv('IS_VIRTUAL_HOST', 'proxyvirtualhost')
IS_VIRTUAL_PORT = os.getenv('IS_VIRTUAL_PORT', 'proxyvirtualport')

SAP_USERNAME = os.getenv('SAP_MID_ODATA_USER')
SAP_PASSWORD = os.getenv('SAP_ODATA_PASSWORD')
SAP_CLIENT = os.getenv('SAP_ODATA_CLIENT')
SAP_LANGUAGE = os.getenv('SAP_LANGUAGE', 'EN')
SAP_AUTH_URL = os.getenv('SAP_MID_AUTH_URL', 'https://sap-auth-url')
SAP_BASE_URL = os.getenv('SAP_MID_BASE_URL', 'https://sap-base-url')
