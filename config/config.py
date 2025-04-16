import os
import json
import gspread

from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CONFIG_DIR, '..', '.env'))
config_path = os.path.join(CONFIG_DIR, 'config.json')

GOOGLE_API_CREDS_DIR = os.path.dirname(os.path.abspath(__file__))
google_api_creds = os.path.join(GOOGLE_API_CREDS_DIR, 'google-api-key.json')

with open(google_api_creds, 'r') as file:
    creds_dict = json.load(file)

with open(config_path, 'r') as file:
    json_config = json.load(file)

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/bigquery'
]

creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
GOOGLE_CLIENT = gspread.authorize(creds)
BQ_CLIENT = bigquery.Client(credentials=creds, project=creds.project_id)

COMPANY_CODE = json_config.get('COMPANY_CODE')
USER_ID = json_config.get('USER_ID')
LAN_TYPE = json_config.get("LAN_TYPE")
API_CERT_KEY = os.getenv('API_CERT_KEY')
SHEET_NAME = json_config.get('SHEET_NAME')
WORKSHEET_NAME = json_config.get('INGESTION_WORKSHEET_NAME')
GCLOUD_PROJECT_ID = json_config.get('BIGQUERY_INFO')['project_id']
BQ_DATASET_NAME = json_config.get('BIGQUERY_INFO')['dataset_name']
BQ_TABLE_NAME = json_config.get('BIGQUERY_INFO')['table_name']

REQUEST_DELAY = 5