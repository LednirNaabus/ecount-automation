import json
import time
import pandas as pd
import logging
from typing import Optional, Any, Dict

from dateutil import parser
from ecount.api import get_zone, login_ecount, get_item_balance_by_location
from utils.exporter import export_to_df
from utils.bq_utils import load_data_to_bq
from config import config
from utils.logger import EcountLogger

ecount_logger = EcountLogger(name="EcountLogger", filename="run.log", mode="w", level=logging.DEBUG)

def has_inventory_data(response):
    if response["Data"]["Result"]:
        return True
    else:
        return False

def login():
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
        ecount_logger.error("No SESSION_ID found.")

    return zone, session_id

def get_formatted_date(base_date):
    parsed_date = parser.parse(base_date)
    return parsed_date.strftime("%Y%m%d")

def load_warehouse_config() -> Optional[dict]:
    try:
        with open('config/config.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        ecount_logger.error(f"Error reading config file: {e}")
        return None

def process_warehouses(zone: str, session_id: str, warehouses: Dict[str, Any], formatted_date: str) -> list[str] | pd.DataFrame:
    empty_warehouses = []
    dataframe_list = []
    warehouse = warehouses.get("Warehouses", {}).items()
    for i, (warehouse_code, warehouse_name) in enumerate(warehouse):
        ecount_logger.info(f"Processing {warehouse_name}...")
        if i > 0:
            ecount_logger.info(f"Waiting {config.REQUEST_DELAY} seconds before next request...")
            time.sleep(config.REQUEST_DELAY)

        inventory_data = fetch_data(zone, session_id, formatted_date, warehouse_code)

        if inventory_data:
            if has_inventory_data(inventory_data):
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

def fetch_data(zone, session_id, formatted_date, warehouse_code):
    return get_item_balance_by_location(
        base_date=formatted_date,
        zone=zone,
        session_id=session_id,
        is_single=False,
        warehouse_code=warehouse_code
    )

def report_empty_warehouse(empty_warehouses) -> list:
    lst = []
    if empty_warehouses:
        for warehouse in empty_warehouses:
            lst.append(warehouse)
    return lst

def run():
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
    
    empty_warehouses, df = process_warehouses(zone, session_id, warehouses, formatted_date)
    total_warehouses = len(warehouses.get("Warehouses", {}))
    if len(empty_warehouses) == total_warehouses:
        ecount_logger.info("API response returns empty data for all warehouses.")
        return
    
    empty = report_empty_warehouse(empty_warehouses)
    ecount_logger.info(f"Empty Warehouses: {empty}")
    ecount_logger.info("\nDataframe:")
    ecount_logger.info(df)

    ecount_logger.info("Loading data into BigQuery...")
    load_data_to_bq(ecount_logger, df, config.GCLOUD_PROJECT_ID, config.BQ_DATASET_NAME, config.BQ_TABLE_NAME)