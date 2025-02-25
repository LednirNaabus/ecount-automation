import pandas as pd

from config import config

def export_to_google_sheets(file):
    sheet = config.GOOGLE_CLIENT.open("testingv1").sheet1
    df = pd.read_excel(file)
    for col in df.select_dtypes(include=['datetime', 'datetime64[ns]']):
        df[col] = df[col].dt.strftime('%Y-%m-%d')
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())