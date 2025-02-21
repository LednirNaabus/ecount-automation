import pandas as pd
from datetime import datetime

def export_to_excel(data, date, filename):
    print("Creating file...\n")
    df = pd.DataFrame(data["Data"]["Result"])
    df['Date'] = datetime.strptime(date, "%Y%m%d").date()
    return df.to_excel(filename, index=False)