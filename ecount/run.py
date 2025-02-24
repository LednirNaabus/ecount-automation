import json
import time
from dateutil import parser

from ecount.api import get_zone, login_ecount, get_item_balance_by_location
from utils.exporter import export_to_excel
from config import config

def has_inventory_data(response):
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return bool(response)

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

def run():
    zone, session_id = login()

    if not (zone and session_id):
        print("Login failed.")
        return

    parsed_date = parser.parse(config.BASE_DATE)
    formatted_date = parsed_date.strftime("%Y%m%d")

    try:
        with open('config/config.json', 'r') as file:
            warehouses = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}")
        return
    
    empty_warehouses = []

    for warehouse_code, warehouse_name in warehouses.get("Warehouses", {}).items():
        print(f"\nProcessing {warehouse_name}.")

        if warehouse_code != list(warehouses.get("Warehouses", {}).keys())[0]:
            print(f"Waiting {config.REQUEST_DELAY} seconds before next request...")
            time.sleep(config.REQUEST_DELAY)
        
        get_item_response = get_item_balance_by_location(
            base_date=formatted_date,
            zone=zone,
            session_id=session_id,
            is_single=False,
            warehouse_code=warehouse_code
        )

        if get_item_response:
            if has_inventory_data(get_item_response):
                filename = f"inventory_balance-{warehouse_name}-{formatted_date}.xlsx"
                filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
                export_to_excel(get_item_response, formatted_date, filename)
                print(f"Successfully exported data for {warehouse_code}: {warehouse_name}.")
            else:
                empty_warehouses.append(warehouse_name)
                print(f"No data found for {warehouse_name}.")
        else:
            print(f"Failed to retrieve API data.")

        if empty_warehouses:
            print("Warehouse(s) with no data:")
            for warehouse in empty_warehouses:
                print(f"{warehouse}")