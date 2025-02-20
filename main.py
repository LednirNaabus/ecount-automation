import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

COMPANY_CODE = os.getenv("COMPANY_CODE")
USER_ID = os.getenv("USER_ID")
API_CERT_KEY = os.getenv("API_CERT_KEY")
LAN_TYPE = os.getenv("LAN_TYPE")

# Get zone
def get_zone(company_code):
    api_url = "https://sboapi.ecount.com/OAPI/V2/Zone"
    payload = {
        "COM_CODE" : company_code
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None
    
# Login
def login_ecount(company_code, user_id, api_cert_key, lang, zone):
    api_url = f"https://sboapi{zone}.ecount.com/OAPI/V2/OAPILogin"
    payload = {
        "COM_CODE" : company_code,
        "USER_ID" : user_id,
        "API_CERT_KEY" : api_cert_key,
        "LAN_TYPE" : lang,
        "ZONE" : zone
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None
    
# Get Item
def get_item_balance_by_location(product_code, base_date, zone, session_id):
    api_url = f"https://sboapi{zone}.ecount.com/OAPI/V2/InventoryBalance/ViewInventoryBalanceStatusByLocation?SESSION_ID={session_id}"
    payload = {
        "PROD_CD" : product_code,
        "BASE_DATE" : base_date
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None
    
# Start with obtaining the zone
zone_response = get_zone(COMPANY_CODE)
if zone_response and "Data" in zone_response:
    zone = zone_response["Data"].get("ZONE")
    print(f"ZONE: {zone}")
    print(f"Logging in...\n")
    # Login and obtain session ID
    login_response = login_ecount(company_code=COMPANY_CODE, user_id=USER_ID, api_cert_key=API_CERT_KEY, lang=LAN_TYPE, zone=zone)
    if login_response and "Data" in login_response and "Datas" in login_response["Data"]:
        datas = login_response["Data"]["Datas"]
        session_id = datas.get("SESSION_ID")
        print(f"SESSION_ID: {session_id}")

        if session_id:
            # Sample product
            product_code = "1034"
            base_date = "20250116"
            get_item_response = get_item_balance_by_location(product_code=product_code, base_date=base_date, zone=zone, session_id=session_id)

            if get_item_response:
                print(json.dumps(get_item_response, indent=2, ensure_ascii=False))
            else:
                print("Failed to retrieve API data.")
        else:
            print("No SESSION_ID found.")
else:
    print("No zone found.")