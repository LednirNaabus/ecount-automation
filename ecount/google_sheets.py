import pandas as pd
import gspread
import time

from config import config

def export_to_google_sheets(file):
    sheet = config.GOOGLE_CLIENT.open(config.SHEET_NAME)
    all_sheets = pd.read_excel(file, sheet_name=None)
    sheet_names = []
    for sheet_name, df in all_sheets.items():
        for col in df.select_dtypes(include=['datetime', 'datetime64[ns]']):
            df[col] = df[col].dt.strftime('%Y-%m-%d')

        if "date" in df.columns:
            date_index = df.columns.get_loc("date") + 1

            new_columns = [
                "starting_balance",
                "ending_balance",
                "stock_in",
                "stock_out"
            ]

            for i, col_name in enumerate(new_columns):
                df.insert(date_index + i, col_name, "")

        try:
            worksheet = sheet.worksheet(sheet_name)
        except Exception:
            worksheet = sheet.add_worksheet(title=sheet_name, rows=str(len(df) + 10), cols=str(len(df.columns) + 10))
        
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        sheet_names.append(sheet_name)
    return sheet_names

def create_ingested_sheet(sheet_names):
    sheet = config.GOOGLE_CLIENT.open(config.SHEET_NAME)

    col_to_extract = ["B2:B", "H2:H", "C2:E", "J2:K", "I2:I", "G2:G", "F2:F"]
    filter_condition = "B2:B<>\"\""

    formula_parts = []
    for sheet_name in sheet_names:
        sheet_ranges = ", ".join([f"'{sheet_name}'!{col}" for col in col_to_extract])
        formula_parts.append(f"FILTER({{{sheet_ranges}}}, '{sheet_name}'!{filter_condition})")

    arrayformula = f"=ARRAYFORMULA(VSTACK({', '.join(formula_parts)}))"
    month_year_formula = '=ARRAYFORMULA(IF(C2:C<>"", TEXT(I2:I, "YYYY-MM"), ""))'

    try:
        print("Opening sheet named 'ingested_sheet'...")
        ingested_sheet = sheet.worksheet(config.WORKSHEET_NAME)
    except Exception:
        ingested_sheet = sheet.add_worksheet(title=config.WORKSHEET_NAME, rows="1000", cols="26")
        print("No sheet named 'ingested_sheet' found. Creating one...")

    headers = [
    "warehouse",
    "starting_balance",
    "item_code",
    "item_name",
    "spec",
    "stock_in",
    "stock_out",
    "ending_balance",
    "date",
    "balance",
    "month_year"
    ]

    ingested_sheet.clear()
    ingested_sheet.update("A1:K1", [headers])
    ingested_sheet.update("A2", [[arrayformula]], raw=False)
    ingested_sheet.update("K2", [[month_year_formula]], raw=False)