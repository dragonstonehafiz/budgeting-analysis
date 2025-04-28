# Spending Dashboard

A Streamlit-based tool for tracking, analyzing, and visualizing personal spending data.\
This app loads purchase records from a structured `.xlsx` file, supports interactive filtering, and generates detailed visual insights.

![Preview Image](images/budgeting1.png)

## Features

- **User Interface (Streamlit)**

  - Full view, yearly view, and search view for flexible data exploration.
  - Filters by category, cost range, date range, and item name.
  - Summarized insights such as top items, spending trends, and category breakdowns.

- **Visualization (Plotly)**

  - Interactive line charts, bar charts, pie charts, and scatter plots.
  - Custom color mapping by category.
  - Auto-filling missing combinations to maintain consistent trend graphs.

- **Excel File Handling (openpyxl)**

  - Prepares an Excel file with auto-formatted columns.
  - Applies conditional formatting based on category.
  - Adds dropdown validation for category selection.
  - Auto-fills Month, Month Number, and Year fields based on purchase dates.

## Folder Structure

```plaintext
├── data/
│   └── purchases.xlsx
├── metadata/
│   └── categories.csv
├── src/
│   ├── streamlit_init.py
│   ├── streamlit_render.py
│   ├── data_classification.py
│   ├── data_processing.py
│   ├── plots.py
│   ├── xlsx_handler.py
│   └── xlsx_formats.py
├── app.py
├── remake_xlsx.py
├── requirements.txt
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dragonstonehafiz/budgeting-analysis.git
   cd budgeting-analysis
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Prepare your Excel file:

   - Place your raw `purchases.xlsx` file inside the `data/` directory.
   - Then **run** the following command to apply formatting and validation:
     ```bash
     python remake_xlsx.py
     ```

   This will fill in the month and year columns.

5. Run the Streamlit app:

   ```bash
   streamlit run src/app.py
   ```

## Expected purchases.xlsx Structure

The app expects the purchase data to be in the following format:

| Column Name | Type       | Description                                                       |
| ----------- | ---------- | ----------------------------------------------------------------- |
| `Item`      | `str`      | Name or description of the purchased item.                        |
| `Category`  | `str`      | Spending category. Should match one of the predefined categories. |
| `Cost`      | `float`    | Purchase amount in dollars.                                       |
| `Date`      | `datetime` | Date of purchase (formatted as `dd/mm/yyyy`).                     |
| `Month`     | `str`      | Auto-generated month name (e.g., `January`, `February`).          |
| `MonthNum`  | `int`      | Auto-generated month number (1–12).                               |
| `Year`      | `str`      | Auto-generated year (e.g., `2025`).                               |

- Columns `Month`, `MonthNum`, and `Year` are **automatically filled** based on the `Date` field if missing.
- `Category` can be manually entered or validated using a dropdown (provided by the Excel formatting scripts).
- Date must be a proper Excel Date value, not plain text.

Example:

| Item             | Category              | Cost   | Date       | Month    | MonthNum | Year |
| ---------------- | --------------------- | ------ | ---------- | -------- | -------- | ---- |
| Netflix          | Digital Subscriptions | 19.99  | 01/01/2025 | January  | 1        | 2025 |
| Nintendo Switch  | Gaming                | 299.99 | 05/01/2025 | January  | 1        | 2025 |
| McDonald's Lunch | Food & Beverages      | 8.50   | 12/02/2025 | February | 2        | 2025 |

## Requirements

- Python 3.9 or newer

## Notes

- The app operates on **local files only**. No external database or API service is required.
- The Excel reformatting scripts can be used to initialize or clean up your `purchases.xlsx` file structure if needed.
- The project does not include user authentication or file uploads.

