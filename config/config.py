import os
import json
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CONFIG_DIR, '..', '.env'))
config_path = os.path.join(CONFIG_DIR, 'config.json')

GOOGLE_API_CREDS_DIR = os.path.dirname(os.path.abspath(__file__))
google_api_creds = os.path.join(GOOGLE_API_CREDS_DIR, 'google-api-key.json')

with open(config_path, 'r') as file:
    json_config = json.load(file)

SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(google_api_creds, SCOPE)
GOOGLE_CLIENT = gspread.authorize(creds)

COMPANY_CODE = json_config.get('COMPANY_CODE')
USER_ID = json_config.get('USER_ID')
LAN_TYPE = json_config.get("LAN_TYPE")
API_CERT_KEY = os.getenv('API_CERT_KEY')

REQUEST_DELAY = 5
BASE_DATE = json_config.get('BASE_DATE')