import pandas as pd
import openpyxl

from src.xlsx_handler import xlsx_init_column, xlsx_format_rows, xlsx_create_category_dv, xlsx_create_category_cf

# Load XLSX
xlsx_path = "data/purchases.xlsx"
wb = openpyxl.load_workbook(xlsx_path)
ws = wb.worksheets[0]
ws.auto_filter.ref = "A1:G1"

# Set column defaults
xlsx_init_column(ws, "A", "Item", 15)
xlsx_init_column(ws, "B", "Category", 15)
xlsx_init_column(ws, "C", "Cost", 10)
xlsx_init_column(ws, "D", "Date", 12)
xlsx_init_column(ws, "E", "Month", 7)
xlsx_init_column(ws, "F", "MonthNum", 5)
xlsx_init_column(ws, "G", "Year", 10)
# Create category dropdown
xlsx_create_category_dv(ws, "B")
# Create conditional formatting for category
xlsx_create_category_cf(ws, "B")
# Format rows
xlsx_format_rows(ws)

# Save
wb.save(xlsx_path)