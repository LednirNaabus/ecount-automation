import base64
import json
import time
import pandas as pd
import logging
import streamlit as st
from typing import Union, Optional, Any, Dict, Tuple
from google.cloud import bigquery
from datetime import datetime

from dateutil import parser
from ecount.api import get_zone, login_ecount, get_item_balance_by_location
from utils.async_utils import run_async
from utils.exporter import export_to_df
from utils.compute import apply_computation_stock
from utils.bq_utils import load_data_to_bq, sql_query_bq, generate_schema
from config import config
from utils.logger import EcountLogger

ecount_logger = EcountLogger(name="EcountLogger", filename="run.log", mode="w", level=logging.DEBUG)

# Initialize state sessions
if 'downloaded' not in st.session_state:
    st.session_state['downloaded'] = False

if 'data_fetched' not in st.session_state:
    st.session_state['data_fetched'] = False

if 'df' not in st.session_state:
    st.session_state['df'] = None

if 'empty_warehouses' not in st.session_state:
    st.session_state['empty_warehouses'] = None

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

@st.cache_data
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
        return zone, None

    session_id = login_response["Data"]["Datas"].get("SESSION_ID")
    ecount_logger.info(f"SESSION_ID: {session_id}")

    if not session_id:
        ecount_logger.error("No `SESSION_ID` found.")

    return zone, session_id

@st.cache_data
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

@st.cache_data
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
                df = export_to_df(inventory_data, formatted_date)
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
            - Schema for the response: WH_CD, WH_DES, PROD_CD, PROD_DES, PROD_SIZE_DES, BAL_QTY
    """
    return get_item_balance_by_location(
        base_date=formatted_date,
        zone=zone,
        session_id=session_id,
        is_single=False,
        warehouse_code=warehouse_code
    )

@st.cache_data
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

def get_download_link(df: pd.DataFrame, filename: str = "data.csv") -> str:
    """
    Generate a download link for a dataframe.

    Parameters:
        df (pd.DataFrame): A pandas dataframe to be read.
        filename (str): The file name; Default is 'data.csv'.

    Returns:
        href (str): A string representing the generated link for the download file.
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

@st.cache_data
def get_cached_warehouse_data(zone: str, session_id: str, warehouses: str, formatted_date: str) -> tuple[list[str], pd.DataFrame]:
    """
    Runs and caches the result of the asynchronous `process_warehouses` function.

    This function wraps `process_warehouses()` using `run_async()` to execute
    the async logic in a synchronous context. The result is cached with
    Streamlit's `@st.cache_data` to avoid redundant computations on reruns.

    Parameters:
        zone (str): The zone string used for this session.
        session_id (str): The session ID retrieved from the login; used for authentication.
        warehouses (str): A string (likely JSON or comma-separated) representing warehouses to process.
        formatted_date (str): The date used for querying or labeling, formatted as `YYYY/MM/DD`.

    Returns:
        tuple[list[str], pd.DataFrame]: 
            - A list of warehouse identifiers that are empty.
            - A pandas DataFrame containing the processed warehouse data.
    """
    return run_async(process_warehouses, zone, session_id, warehouses, formatted_date)

def download_callback():
    """
    This function sets a flag in `st.session_state` to indicate that the 
    download has been triggered. It can be used to control UI behavior or 
    conditional logic (e.g. show a message or trigger another process).

    Side Effects:
        Sets `st.session_state.downloaded` to True.
    """
    st.session_state.downloaded = True

def run():
    st.title("GoParts Data")
    zone, session_id = login()

    if not (zone and session_id):
        st.write("Login failed. Try again.")
        ecount_logger.error("Login failed.")
        return

    ecount_logger.info("Login success!")

    date_input = st.date_input(label="Enter base date:")
    formatted_base_date = get_formatted_date(str(date_input))
    ecount_logger.info("Loading warehouse configuration file...")
    warehouses = load_warehouse_config()
    if not warehouses:
        return

    if st.button("Submit"):
    
        if not st.session_state['data_fetched']:
            with st.spinner("Fetching data..."):
                empty_warehouses, df = get_cached_warehouse_data(zone, session_id, warehouses, formatted_base_date)
                total_warehouses = len(warehouses.get("Warehouses", {}))
                if len(empty_warehouses) == total_warehouses:
                    ecount_logger.info("API response returned empty data for all warehouses.")
                    return
        else:
            df = st.session_state['df']
            empty_warehouses = df.session_state['empty_warehouses']

        st.success("Data fetched!")
        st.dataframe(df)
        st.write(f"Empty Warehouses: {empty_warehouses}")

        empty = report_empty_warehouse(empty_warehouses)
        ecount_logger.info(f"Empty Warehouses: {empty}")
        ecount_logger.info("\nDataframe:")
        ecount_logger.info(df)
        
        csv = df.to_csv(index=False).encode('utf-8')

        if not st.session_state['downloaded']:
            st.download_button("Download", csv, "data.csv", "text/csv", key='download_button', on_click=download_callback)
        else:
            st.success("File Downloaded.")
            st.button("Download again", key="download_again")
            st.session_state['downloaded'] = False

        # If user clicks download button, Streamlit will re-run the app
        # With that context in mind, load_data_to_bq() will re-run as well
        ecount_logger.info("Loading data into BigQuery...")
        with st.spinner("Loading data into BigQuery, please wait before making another request.", show_time=True):
            schema1 = generate_schema(df)
            load_data_to_bq(ecount_logger, df, config.GCLOUD_PROJECT_ID, config.BQ_DATASET_NAME, config.BQ_TABLE_NAME, schema=schema1)
            df1 = sql_query_bq(f"SELECT * FROM `{config.GCLOUD_PROJECT_ID}.{config.BQ_DATASET_NAME}.{config.BQ_TABLE_NAME}`")
            new_df = apply_computation_stock(df1)
            schema2 = generate_schema(new_df)
            load_data_to_bq(ecount_logger, new_df, config.GCLOUD_PROJECT_ID, config.BQ_DATASET_NAME, config.BQ_TABLE_NAME, write_mode="WRITE_TRUNCATE", schema=schema2)