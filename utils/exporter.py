import pandas as pd
from datetime import datetime
from typing import Literal, Any, Dict

def export_to_excel(writer, data, warehouse_name, date, file_ext: Literal['.xlsx', '.csv']):
    sheet_name = "".join(c for c in warehouse_name if c.isalnum() or c in (' ', '_', '-'))[:31]
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    if file_ext == '.xlsx':
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    elif file_ext == '.csv':
        df.to_csv(f"inventory_balance_{warehouse_name}_asof_{date}.csv", index=False)

def export_to_df(data: Dict[str, Any], warehouse_name: str, date: str) -> pd.DataFrame:
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['month_year'] = df['Date'].dt.to_period('M')
    df['stock_in'] = 0
    df['stock_out'] = 0

    df = df.drop("WH_CD", axis='columns')
    df = df.rename(columns={
        "WH_DES" : "warehouse",
        "PROD_CD" : "item_code",
        "PROD_DES" : "item_name",
        "PROD_SIZE_DES" : "spec",
        "BAL_QTY" : "balance"
    })   
    return df