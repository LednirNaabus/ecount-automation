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

def stock_in_out(row, prev_qty):
    if row['BAL_QTY'] > row['stock_in']:
        row['stock_in'] = row['BAL_QTY']
        row['stock_out'] = 0

    if row['BAL_QTY'] > row['stock_out']:
        row['stock_out'] = row['BAL_QTY'] - prev_qty
        row['stock_in'] = 0

    return row

# item_code, warehouse, and date
def export_to_df(data: Dict[str, Any], date: str) -> pd.DataFrame:
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    df['Date'] = pd.to_datetime(df['Date'])
    df['month_year'] = df['Date'].dt.to_period('M').dt.to_timestamp().dt.date
    df['BAL_QTY'] = pd.to_numeric(df['BAL_QTY'])
    # df['stock_in'] = 0
    # df['stock_in'] = np.where(df['BAL_QTY'] > df['stock_in'], df['BAL_QTY'], 0)
    # df['stock_out'] = 0
    # df['stock_out'] = np.where(df['BAL_QTY'] > df['stock_out'], df['BAL_QTY']-df['BAL_QTY'].shift(1), 0)
    # df['stock_in'] = 0
    # df['stock_out'] = 0
    df['stock_in'] = 0
    df['stock_out'] = 0

    prev_qty = df['BAL_QTY'].shift(1).fillna(0)
    df = df.apply(lambda row: stock_in_out(row, prev_qty[row.name]), axis=1)

    # df['stock_in'] = df.apply(stock_in_out, axis=1)
    # df['stock_out'] = df.apply(stock_in_out, axis=1)

    df = df.drop("WH_CD", axis='columns')
    df = df.rename(columns={
        "WH_DES" : "warehouse",
        "PROD_CD" : "item_code",
        "PROD_DES" : "item_name",
        "PROD_SIZE_DES" : "spec",
        "BAL_QTY" : "balance"
    })   
    return df