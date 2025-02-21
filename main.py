import json
from datetime import date

from ecount.run import login
from ecount.api import get_item_balance_by_location
from utils.exporter import export_to_excel

def run():
    zone, session_id = login()
    if zone and session_id:
        # Change your search parameters here
        product_code = "1034"
        base_date = date.today()
        # formatted_date = base_date.strftime("%Y%m%d")
        formatted_date = "20250201"
        """
        Base the warehouse code to the Location code found in Ecount
        """
        warehouse_code = "00001" # code for JHM

        # By default fetching item by location is set to all
        # To fetch single item by location set is_single to True
        # NOTE: product_code is required when is_single is set to True
        get_item_response = get_item_balance_by_location(
            base_date=formatted_date,
            zone=zone,
            session_id=session_id,
            is_single=False,
            warehouse_code=warehouse_code
        )

        if get_item_response:
            export_to_excel(get_item_response, formatted_date, f"inventory_balance-{formatted_date}.xlsx")
            print(json.dumps(get_item_response, indent=2, ensure_ascii=False))
        else:
            print("Failed to retrieve API data.")

if __name__ == "__main__":
    run()