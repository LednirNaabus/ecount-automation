import os

from dotenv import load_dotenv
load_dotenv()

COMPANY_CODE = os.getenv("COMPANY_CODE")
USER_ID = os.getenv("USER_ID")
API_CERT_KEY = os.getenv("API_CERT_KEY")
LAN_TYPE = os.getenv("LAN_TYPE")