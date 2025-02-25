import pandas as pd
from datetime import datetime
from typing import Literal

def export_to_excel(writer, data, warehouse_name, date, file_ext: Literal['.xlsx', '.csv']):
    sheet_name = "".join(c for c in warehouse_name if c.isalnum() or c in (' ', '_', '-'))[:31]
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    if file_ext == '.xlsx':
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    elif file_ext == '.csv':
        df.to_csv(f"inventory_balance_{warehouse_name}_asof_{date}.csv", index=False)