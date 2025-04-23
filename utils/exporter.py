import pandas as pd
import numpy as np
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

def export_to_df(data: Dict[str, Any], date: str) -> pd.DataFrame:
    df = pd.DataFrame(data["Data"]["Result"])
    df['date'] = datetime.strptime(date, "%Y%m%d").date()
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M').dt.to_timestamp().dt.date
    df['BAL_QTY'] = pd.to_numeric(df['BAL_QTY'])
    df = df.sort_values(by='date')
    df[['stock_in', 'stock_out']] = 0

    df.drop(columns=['WH_CD'], inplace=True)
    df = df.rename(columns={
        "WH_DES" : "warehouse",
        "PROD_CD" : "item_code",
        "PROD_DES" : "item_name",
        "PROD_SIZE_DES" : "spec",
        "BAL_QTY" : "balance"
    })   
    return df