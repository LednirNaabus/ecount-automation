import pandas as pd
from datetime import datetime
from typing import Literal

def export_to_excel(data, warehouse_name, date, file_ext: Literal['.xlsx', '.csv']):
    print("Creating file...\n")
    filename = f"inventory_balance_{warehouse_name}_asof_{date}.{file_ext}"
    filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    return df.to_excel(filename, index=False)