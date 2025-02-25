import pandas as pd

from config import config

def export_to_google_sheets(file):
    sheet = config.GOOGLE_CLIENT.open("testingv1")
    all_sheets = pd.read_excel(file, sheet_name=None)
    for sheet_name, df in all_sheets.items():
        for col in df.select_dtypes(include=['datetime', 'datetime64[ns]']):
            df[col] = df[col].dt.strftime('%Y-%m-%d')

        try:
            worksheet = sheet.worksheet(sheet_name)
        except Exception:
            worksheet = sheet.add_worksheet(title=sheet_name, rows=str(len(df) + 10), cols=str(len(df.columns) + 10))
        
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())