import os
import json

from dotenv import load_dotenv

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CONFIG_DIR, '..', '.env'))
config_path = os.path.join(CONFIG_DIR, 'config.json')

with open(config_path, 'r') as file:
    json_config = json.load(file)

COMPANY_CODE = json_config.get('COMPANY_CODE')
USER_ID = json_config.get('USER_ID')
LAN_TYPE = json_config.get("LAN_TYPE")
API_CERT_KEY = os.getenv('API_CERT_KEY')

REQUEST_DELAY = 3.8