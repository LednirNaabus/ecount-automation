import asyncio
import json
import time
import pandas as pd
import logging
import streamlit as st
from typing import Union, Optional, Any, Dict, Tuple

from dateutil import parser
from ecount.api import get_zone, login_ecount, get_item_balance_by_location
from utils.exporter import export_to_df
from utils.bq_utils import load_data_to_bq
from config import config
from utils.logger import EcountLogger

ecount_logger = EcountLogger(name="EcountLogger", filename="run.log", mode="w", level=logging.DEBUG)

async def has_inventory_data(response: dict) -> bool:
    """
    Checks if the response contains inventory data.
    
    Parameters:
        response (dict): A dictionary representing the API response.
                        Expected to have the structure `response["Data"]["Result"]`.

    Returns:
        bool: True if `response["Data"]["Result"]` contains data, otherwise returns False.
    """
    if response["Data"]["Result"]:
        return True
    else:
        return False

def login() -> Tuple[Optional[str], Optional[str]]:
    """
    Logs into the system and retrieves the `zone` and `session_id`.
    Returns:
        tuple: A tuple containing:
            - zone (str or None): The zone string returned from the zone response.
            - session_id (str or None): The session ID from the login response.
    """
    zone_response = get_zone(config.COMPANY_CODE)
    if not zone_response or "Data" not in zone_response:
        ecount_logger.error("No zone found.")
        return None, None
    
    zone = zone_response["Data"].get("ZONE")
    ecount_logger.info(f"ZONE: {zone}")
    ecount_logger.info(f"Logging in...\n")

    login_response = login_ecount(
        config.COMPANY_CODE,
        config.USER_ID,
        config.API_CERT_KEY,
        config.LAN_TYPE,
        zone
    )

    if not login_response or "Data" not in login_response or "Datas" not in login_response["Data"]:
        ecount_logger.error("Login failed.")
        return zone, None

    session_id = login_response["Data"]["Datas"].get("SESSION_ID")
    ecount_logger.info(f"SESSION_ID: {session_id}")

    if not session_id:
        ecount_logger.error("No `SESSION_ID` found.")

    return zone, session_id

def get_formatted_date(base_date: str) -> str:
    """
    Parses a date string and returns it in `YYYY/MM/DD` format.
    Parameters:
        base_date (str): A date string to parse.

    Returns:
        str: The formatted date string in `YYYY/MM/DD` format.
    """
    parsed_date = parser.parse(base_date)
    return parsed_date.strftime("%Y%m%d")

def load_warehouse_config() -> Optional[dict]:
    """
    Loads and parses the warehouse JSON configuration file.

    Returns:
        Optional[dict]: The parsed JSON content of the configuration file. Returns None if there is an error reading the file.
    """
    try:
        with open('config/config.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        ecount_logger.error(f"Error reading config file: {e}")
        return None

@st.cache_resource
async def process_warehouses(zone: str, session_id: str, warehouses: Dict[str, Any], formatted_date: str) -> list[str] | pd.DataFrame:
    """
    Processes the data loaded from the warehouse configuration file and returns a list of empty warehouses and a pandas DataFrame of warehouses that contain data.

    For each warehouse, this function does the following:
    1. Fetches inventory data using the provided credentials (`zone`, `session_id`, `formatted_date`).
    2. If data is found and valid, it exports to a pandas DataFrame.
    3. If no data is found, it appends the warehouse name to the `empty_warehouse` list.
    4. Returns a DataFrame of combined data if any warehouses had valid inventory data.
    5. If all warehouses returned empty, returnes a DataFrame with a single entry indicating empty data.

    Parameters:
        zone (str): The zone identifier for the session.
        session_id (str): The session ID retrieved from the login; used for authentication.
        warehouses (Dict[str, Any]): A dictionary containing warehouse data.
        formatted_date (str): The date used for querying or labeling, formatted as `YYYY/MM/DD`.

    Returns:
        Union[list[str], pd.DataFrame]:
            - empty_warehouses: A list of empty warehouses.
            - combined_df: A pandas DataFrame with the processed warehouse data.
    """
    empty_warehouses = []
    dataframe_list = []
    warehouse = warehouses.get("Warehouses", {}).items()
    for i, (warehouse_code, warehouse_name) in enumerate(warehouse):
        ecount_logger.info(f"Processing {warehouse_name}...")
        if i > 0:
            ecount_logger.info(f"Waiting {config.REQUEST_DELAY} seconds before next request...")
            time.sleep(config.REQUEST_DELAY)

        inventory_data = await fetch_data(zone, session_id, formatted_date, warehouse_code)

        if inventory_data:
            if await has_inventory_data(inventory_data):
                df = export_to_df(inventory_data, warehouse_name, formatted_date)
                dataframe_list.append(df)
                ecount_logger.info(f"Exported data for {warehouse_code}:{warehouse_name}")
            else:
                empty_warehouses.append(warehouse_name)
                ecount_logger.info(f"No data found for {warehouse_name}")
    
    if dataframe_list:
        combined_df = pd.concat(dataframe_list, ignore_index=True)
    else:
        ecount_logger.info("All warehouses returned empty data.")
        combined_df = pd.DataFrame(["Empty"])

    return empty_warehouses, combined_df

@st.cache_resource
async def fetch_data(zone: str, session_id: str, formatted_date: str, warehouse_code: str) -> Union[Dict[str, Any], None]:
    """
    Calls the `get_item_balance_by_location()` function from `api.py` with the provided parameters and returns its result. Refer to documentation of `get_item_balance_by_location()` for more information.

    Parameters:
        zone (str): The zone string used for this session.
        session_id (str): The session ID retrieved from the login; used for authentication.
        formatted_date (str): The date used for querying or labeling, formatted as `YYYY/MM/DD`.
        warehouse_code (str): The unique warehouse identifier.

    Returns:
        Union[Dict[str, Any], None]:
            - A dictionary representing the parsed JSON data from the response if available.
            - None if no data is available or an error occurs in `get_item_balance_by_location()`.
    """
    return get_item_balance_by_location(
        base_date=formatted_date,
        zone=zone,
        session_id=session_id,
        is_single=False,
        warehouse_code=warehouse_code
    )

def report_empty_warehouse(empty_warehouses: str) -> list:
    """
    Stores a list of empty warehouses.

    Parameters:
        empty_warehouses (str): Name of warehouse that did not return any data.

    Returns:
        lst (list[str]): A list of empty warehouses.
    """
    lst = []
    if empty_warehouses:
        for warehouse in empty_warehouses:
            lst.append(warehouse)
    return lst

def run_async(coroutine):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        future = asyncio.ensure_future(coroutine)
        return asyncio.get_event_loop().run_until_complete(future)
    else:
        return loop.run_until_complete(coroutine)

def run():
    st.title("GoParts Data")
    ecount_logger.info("Logging in...")
    zone, session_id = login()

    if not (zone and session_id):
        ecount_logger.error("Login failed.")
        return

    ecount_logger.info("Login success!")

    formatted_date = get_formatted_date(config.BASE_DATE)
    ecount_logger.info("Loading warehouse configuration file...")
    warehouses = load_warehouse_config()
    if not warehouses:
        return
    
    with st.spinner("Fetching data..."):
        empty_warehouses, df = run_async(process_warehouses(zone, session_id, warehouses, formatted_date))
        total_warehouses = len(warehouses.get("Warehouses", {}))
        if len(empty_warehouses) == total_warehouses:
            ecount_logger.info("API response returns empty data for all warehouses.")
            return

    st.success("Data fetched!")
    st.dataframe(df)
    st.write(f"Empty Warehouses: {empty_warehouses}")

    empty = report_empty_warehouse(empty_warehouses)
    ecount_logger.info(f"Empty Warehouses: {empty}")
    ecount_logger.info("\nDataframe:")
    ecount_logger.info(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download", csv, "data.csv", "text/csv")

    ecount_logger.info("Loading data into BigQuery...")
    # load_data_to_bq(ecount_logger, df, config.GCLOUD_PROJECT_ID, config.BQ_DATASET_NAME, config.BQ_TABLE_NAME)