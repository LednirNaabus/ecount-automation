import json
import time
import pandas as pd

from dateutil import parser
from ecount.api import get_zone, login_ecount, get_item_balance_by_location
from ecount.google_sheets import export_to_google_sheets, create_ingested_sheet, validate_file, check_spreadsheet
from utils.exporter import export_to_excel
from config import config

def has_inventory_data(response):
    if response["Data"]["Result"]:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return True
    else:
        print(f"No Data: {response["Data"]["Result"]}")
        return False

def login():
    zone_response = get_zone(config.COMPANY_CODE)
    if not zone_response or "Data" not in zone_response:
        print("No zone found.")
        return None, None
    
    zone = zone_response["Data"].get("ZONE")
    print(f"ZONE: {zone}")
    print(f"Logging in...\n")

    login_response = login_ecount(
        config.COMPANY_CODE,
        config.USER_ID,
        config.API_CERT_KEY,
        config.LAN_TYPE,
        zone
    )

    if not login_response or "Data" not in login_response or "Datas" not in login_response["Data"]:
        print("Login failed.")
        return zone, None

    session_id = login_response["Data"]["Datas"].get("SESSION_ID")
    print(f"SESSION_ID: {session_id}")

    if not session_id:
        print("No SESSION_ID found.")

    return zone, session_id

def get_formatted_date(base_date):
    parsed_date = parser.parse(base_date)
    return parsed_date.strftime("%Y%m%d")

def load_warehouse_config():
    try:
        with open('config/config.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}")
        return None

def process_warehouses(zone, session_id, warehouses, formatted_date, filename):
    empty_warehouses = []
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        warehouse = warehouses.get("Warehouses", {}).items()
        
        for i, (warehouse_code, warehouse_name) in enumerate(warehouse):
            print(f"\nProcessing {warehouse_name}...")

            if i > 0:
                print(f"Waiting {config.REQUEST_DELAY} seconds before next request...")
                time.sleep(config.REQUEST_DELAY)
            
            inventory_data = fetch_data(zone, session_id, formatted_date, warehouse_code)

            if inventory_data:
                if has_inventory_data(inventory_data):
                    export_to_excel(writer, inventory_data, warehouse_name, formatted_date, file_ext=".xlsx")
                    print(f"Exported data for {warehouse_code}:{warehouse_name}")
                else:
                    empty_warehouses.append(warehouse_name)
                    print(f"No data found for {warehouse_name}")
    
    return empty_warehouses

def fetch_data(zone, session_id, formatted_date, warehouse_code):
    return get_item_balance_by_location(
        base_date=formatted_date,
        zone=zone,
        session_id=session_id,
        is_single=False,
        warehouse_code=warehouse_code
    )

def report_empty_warehouse(empty_warehouses):
    if empty_warehouses:
        print("Warehouse(s) with no data:")
        for warehouse in empty_warehouses:
            print(f"{warehouse}")

def run():
    zone, session_id = login()

    if not (zone and session_id):
        print("Login failed.")
        return

    formatted_date = get_formatted_date(config.BASE_DATE)
    warehouses = load_warehouse_config()
    if not warehouses:
        return
    
    filename = f"inventory_balance_asof_{formatted_date}.xlsx"
    empty_warehouses = process_warehouses(zone, session_id, warehouses, formatted_date, filename)

    print(f"Transferring files to Google Sheets...")
    excel_file = validate_file(filename)
    target_spreadsheet = check_spreadsheet(config.GOOGLE_CLIENT, config.SHEET_NAME)
    exported = export_to_google_sheets(excel_file, target_spreadsheet)
    create_ingested_sheet(target_spreadsheet, exported)
    report_empty_warehouse(empty_warehouses)