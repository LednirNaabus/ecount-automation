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

def compute_stock(row):
    if pd.isna(row['prev_balance']):
        return pd.Series({
            'stock_in': row['BAL_QTY'],
            'stock_out': 0
        })
    elif row['BAL_QTY'] > row['prev_balance']:
        return pd.Series({
            'stock_in': row['BAL_QTY'] - row['prev_balance'],
            'stock_out': 0
        })
    elif row['BAL_QTY'] < row['prev_balance']:
        return pd.Series({
            'stock_in': 0,
            'stock_out': row['prev_balance'] - row['BAL_QTY']
        })

    else:
        return pd.Series({
            'stock_in': 0,
            'stock_out': 0
        })
    pass

# item_code, warehouse, and date
def export_to_df(data: Dict[str, Any], date: str) -> pd.DataFrame:
    df = pd.DataFrame(data["Data"]["Result"])
    df['date'] = datetime.strptime(date, "%Y%m%d").date()
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M').dt.to_timestamp().dt.date
    df['BAL_QTY'] = pd.to_numeric(df['BAL_QTY'])

    df = df.sort_values(by=['PROD_CD', 'date'])
    df['prev_balance'] = df.groupby('PROD_CD')['BAL_QTY'].shift(1)

    # compute stock
    df[['stock_in', 'stock_out']] = df.apply(compute_stock, axis=1)

    df.drop("WH_CD", axis='columns')
    df.drop(columns='prev_balance', inplace=True)
    df = df.rename(columns={
        "WH_DES" : "warehouse",
        "PROD_CD" : "item_code",
        "PROD_DES" : "item_name",
        "PROD_SIZE_DES" : "spec",
        "BAL_QTY" : "balance"
    })   
    return df