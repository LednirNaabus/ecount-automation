import requests

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
    
def get_item_balance_by_location(base_date, zone, session_id, is_single=True, warehouse_code=None, product_code=None):
    if is_single:
        if product_code is None:
            raise ValueError("product_code must be provided when is_single is set to True.")
        api_url = f"https://sboapi{zone}.ecount.com/OAPI/V2/InventoryBalance/ViewInventoryBalanceStatusByLocation?SESSION_ID={session_id}"
        payload = {
            "PROD_CD": product_code,
            "BASE_DATE": base_date
        }
    else:
        if warehouse_code is None:
            raise ValueError("warehouse_code must be provided when is_single is False.")
            
        api_url = f"https://sboapi{zone}.ecount.com/OAPI/V2/InventoryBalance/GetListInventoryBalanceStatusByLocation?SESSION_ID={session_id}"
        payload = {
            "BASE_DATE": base_date,
            "WH_CD": warehouse_code
        }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None