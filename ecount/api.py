import requests
import streamlit as st
from typing import Optional, Dict, Any

@st.cache_data
def get_zone(company_code: str) -> Optional[Dict[str, Any]]:
    """
    Sends a POST request to Ecount `Zone` API. For more documentation about the Ecount OpenAPI, visit their official [documentation](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).

    This function constructs a POST request to a predefined API URL, sending the argument `company_code` as a payload with the key `COM_CODE`.
    If the request is successful, it returns the zone of the company as a dictionary. If the request fails or an error occurs, it logs the exception and returns None.

    Parameters:
        company_code (str): The code associated with the company. The company code is sent in the API request payload under the key `COMPANY_CODE`.

    Returns:
        Optional[Dict[str, Any]]:
            - A dictionary representing the parsed JSON response from the Ecount OpenAPI if the request is successful.
            - None if the request fails or an exception is raised.
    """
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
    
@st.cache_data
def login_ecount(company_code: str, user_id: str, api_cert_key: str, lang: str, zone: str) -> Optional[Dict[str, Any]]:
    """
    Sends a POST request to Ecount `Login` API. For more documentation about the Ecount OpenAPI, visit their official [documentation](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).

    This function constructs a POST request to a predefined API URL, sending the arguments as a payload with the following keys:

    - `COM_CODE`
    - `USER_ID`
    - `API_CERT_KEY`
    - `LAN_TYPE`
    - `ZONE`

    If the request is successful, it returns the company code, user ID, and session ID.

    Parameters:
        company_code (str): The code associated with the company when logging in to Ecount.
        user_id (str): The user ID used logging in to Ecount. The user ID is also connected with the Ecount API Key provided to your account.
        api_cert_key (str): The test authentication key issued through logging in to Ecount.
        lang (str): Language type used. Default is `ko-KR`.
        zone (str): The domain zone.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the parsed JSON response from the API if the request is successful.
    """
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
    
@st.cache_data
def get_item_balance_by_location(base_date: str, zone: str, session_id: str, is_single: bool = True, warehouse_code: str = None, product_code: str = None) -> Optional[Dict[str, Any]]:
    """
    Sends a POST request to Ecount `Inventory Balance` API. It interacts with the `Inventory Balance` API to retrieve data for specified warehouse or product code on a certain date. For more documentation about the Ecount OpenAPI, visit their official [documentation](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).


    By default, `is_single` is set to `True`. If set to `True`, only `product_code` and `base_date` is used to fetch the inventory data otherwise it fetches warehouse data.

    Parameters:
        base_date (str): The date you want to search; Formatted to `YYYY/MM/DD`.
        zone (str): The domain zone.
        session_id (str): The session ID retrieved from the login; used for authentication.
        is_single (bool): Checker for `warehouse_code` or `product_code`.
        warehouse_code (str): Unique code identifier for the location (warehouse) code you want to search.
        product_code (str): Unique code identifier for the item you want to search.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the parsed JSON response from the API if the request is successful.
    """
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