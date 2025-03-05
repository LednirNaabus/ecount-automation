import pandas as pd
import gspread
import time

from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
from config import config

def validate_file(file) -> pd.ExcelFile:
    if not pd.io.common.file_exists(file):
        raise FileNotFoundError(f"Excel file not found: {file}")

    try:
        excel_file = pd.ExcelFile(file)
        if not excel_file.sheet_names:
            raise ValueError(f"No sheets found in the Excel file: {file}")
        return excel_file
    except Exception as e:
        print(f"Error reading file: {e}")

def check_spreadsheet(client, spreadsheet_name):
    try:
        return client.open(spreadsheet_name)
    except SpreadsheetNotFound:
        available_sheets = client.openall()
        print(f"Error: {spreadsheet_name} not found.")
        for sheet in available_sheets:
            print(f"{sheet.title}")
        raise

def export_to_google_sheets(excel_file: pd.ExcelFile, target_spreadsheet: gspread.Spreadsheet):
    exported_sheets = []
    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)
        datetime_columns = df.select_dtypes(include=['datetime', 'datetime64[ns]']).columns
        for col in datetime_columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d')

        try:
            worksheet = target_spreadsheet.worksheet(sheet_name)
        except WorksheetNotFound:
            worksheet = target_spreadsheet.add_worksheet(
                title=sheet_name,
                rows=len(df) + 10,
                cols=len(df.columns) + 10
            )

        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        exported_sheets.append(sheet_name)
        print(f"Exported: {sheet_name}")
    return exported_sheets

def create_ingested_sheet(target_spreadsheet: gspread.spreadsheet, exported_sheets):
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

    try:
        ingested_sheet = target_spreadsheet.worksheet(config.WORKSHEET_NAME)
    except WorksheetNotFound:
        ingested_sheet = target_spreadsheet.add_worksheet(
            title=config.WORKSHEET_NAME,
            rows=1000,
            cols=26
        )

    col_to_extract = ["B2:B", "H2:H", "C2:E", "J2:K", "I2:I", "G2:G", "F2:F"]
    filter_condition = "B2:B<>\"\""

    formula_parts = []
    for sheet_name in exported_sheets:
        sheet_ranges = ", ".join([f"'{sheet_name}'!{col}" for col in col_to_extract])
        formula_parts.append(f"FILTER({{{sheet_ranges}}}, '{sheet_name}'!{filter_condition})")

    arrayformula = f"=ARRAYFORMULA(VSTACK({', '.join(formula_parts)}))"
    month_year_formula = '=ARRAYFORMULA(IF(C2:C<>"", TEXT(I2:I, "YYYY-MM"), ""))'

    ingested_sheet.clear()
    ingested_sheet.update("A1:K1", [headers])
    ingested_sheet.update("A2", [[arrayformula]], raw=False)
    ingested_sheet.update("K2", [[month_year_formula]], raw=False)

    print("Done.")