import openpyxl
import datetime

from src.xlsx_handler import xlsx_init_column, xlsx_format_rows, xlsx_create_category_dv, xlsx_create_category_cf

# Load XLSX
xlsx_path = "data/purchases.xlsx"
wb = openpyxl.load_workbook(xlsx_path)
now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
wb.save(f"data/purchases_backup_{now}.xlsx")

# Create new worksheet
ws = wb.worksheets[0]
ws.auto_filter.ref = "A1:H1"

# Initialize columns
cols = {
    "Item": ["A", 15],
    "Category": ["B", 15],
    "Cost": ["C", 10],
    "Date": ["D", 12],
    "Notes": ["E", 15],
    "Month": ["F", 12],
    "MonthNum": ["G", 5],
    "Year": ["H", 10]
}

# Set column defaults
for col, (col_letter, width) in cols.items():
    xlsx_init_column(ws, col_letter, col, width)


# Create category dropdown
xlsx_create_category_dv(ws, "B")
# Create conditional formatting for category
xlsx_create_category_cf(ws, "B")
# Format rows
xlsx_format_rows(ws, cols)

# Save
wb.save(xlsx_path)