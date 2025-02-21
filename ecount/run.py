from ecount.api import get_zone, login_ecount
from config import config

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