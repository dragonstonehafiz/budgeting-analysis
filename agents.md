# Agents.md - Budgeting Dashboard Application Documentation

> **⚠️ IMPORTANT INSTRUCTION FOR AI AGENTS:**
> 
> **This file MUST be updated whenever code changes are made to this project.**
> - When modifying any source files, update the relevant sections below
> - When adding new features, document them in the appropriate sections
> - When refactoring code, ensure the architecture diagrams remain accurate
> - Keep code examples in sync with actual implementation
> - Update dependencies if requirements.txt changes

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Structure & Responsibilities](#file-structure--responsibilities)
4. [Core Components Deep Dive](#core-components-deep-dive)
5. [Data Flow](#data-flow)
6. [Key Features Implementation](#key-features-implementation)
7. [UI Framework & Design](#ui-framework--design)
8. [Excel File Management](#excel-file-management)
9. [Visualization System](#visualization-system)
10. [Development Guide](#development-guide)
11. [Common Patterns & Conventions](#common-patterns--conventions)

---

## Project Overview

**Budgeting Dashboard** is a desktop application built with **PySide6 (Qt)** that provides comprehensive analysis and visualization of personal spending data stored in Excel format.

### Technology Stack
- **UI Framework:** PySide6 (Qt 6.9.3)
- **Data Processing:** pandas (2.2.3)
- **Excel I/O:** openpyxl (3.1.5)
- **Visualization:** matplotlib (embedded in Qt via FigureCanvasQTAgg)
- **Packaging:** PyInstaller (6.16.0)

### Core Capabilities
1. **Interactive Dashboard** - KPI cards, trend charts, category breakdowns, spending analytics
2. **Searchable Table View** - Sortable, filterable data table with pandas-backed sorting
3. **Excel File Management** - Automated reformatting, backup creation, date-based sorting
4. **Dynamic Filtering** - Year-based and search-based filtering across all views
5. **Interactive Charts** - Hover tooltips, custom annotations, category-colored visualizations

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      qt_app.py (Main)                        │
│  - MainWindow: app entry point, menu                         │
│  - Manages data_dir path (executable-aware)                 │
│  - Directly shows DashboardPage (no navigation)             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  DashboardPage│
         │  (dashboard.py)│
         └───────┬───────┘
                 │
         ┌───────▼──────────────────────────────────┐
         │           Utils Layer                     │
         ├───────────────────────────────────────────┤
         │ data_loader.py    - Excel → DataFrame     │
         │ plots.py          - Matplotlib charts     │
         │ xlsx_handler.py   - Excel write/format    │
         │ xlsx_formats.py   - Openpyxl styles       │
         │ category_colors.py- Color mapping         │
         │ path_helpers.py   - PyInstaller-aware paths│
         └───────────────────────────────────────────┘
```

### Data Flow Diagram

```
Excel File (purchases.xlsx)
         │
         ▼
  [data_loader.load_df()]
         │
         ▼
   pandas DataFrame
         │
         ▼
   Dashboard Page
   - Filters data
   - Computes KPIs
   - Renders charts (matplotlib)
   - Interactive canvas with category colors
         │
         ▼
   User Interactions
```

---

## File Structure & Responsibilities

### Main Application
**`src/qt_app.py`** (120 lines, approximately)
- **Entry Point:** Creates `MainWindow` and runs Qt event loop
- **MainWindow Class:**
  - Menu bar (File → Open Data Folder, Exit; Help → About)
  - Status bar showing current data directory
  - Uses `get_data_folder()` to locate `data/` directory (PyInstaller-aware)
  - Directly displays `DashboardPage` as central widget (no navigation sidebar)
  - Default window size: 1280x720, minimum: 1024x600

### Pages

#### **`src/pages/dashboard.py`** (1182 lines)
Primary analytics interface with four major sections:

1. **Statistics Panel** - 13 KPI cards in 3 rows:
   - Row 1: Total spent, Items bought
   - Row 2: Average spend, quartiles (25th/median/75th), Standard deviation
   - Row 3: Average weekly/monthly/yearly spend, Spending volatility

2. **Overall Data Section:**
   - Chart selector: Monthly trend, Rolling average (3-month), or Cumulative spending
   - Top 10 most expensive items table
   - Category pie chart (donut) + Amount distribution pie chart
   - Top items bar chart with category-colored stacked segments

3. **Monthly Details Section** (visible when year selected):
   - Monthly spending pie chart showing 12-month breakdown
   - Month selector dropdown
   - Items table for selected month (5 columns: Item, Category, Cost, Date, Notes)
   - Category pie chart for selected month
   - Top items bar chart for selected month

4. **Category Section:**
   - Category dropdown selector
   - Top items bar chart filtered by category
   - Top 10 table for selected category

**Key Methods:**
- `set_data(df=None)`: Load data, populate year selector, trigger initial render
- `_compute_and_update(selection_text)`: Apply year and search filters, update all views
- `_update_metrics(df)`: Calculate 13 KPI values from filtered DataFrame
- `_render_monthly_overview(df_sel)`: Create trend/rolling average chart + tables
- `_render_monthly_details(df_sel)`: Build month pie + items table
- `_render_category_details(df_sel)`: Update category chart and table
- `_on_remake_clicked()`: Trigger `remake_xlsx_file()` with confirmation dialog

### Utilities

#### **`src/utils/data_loader.py`** (65 lines)
Single function: `load_df(filepath: str | Path) -> pd.DataFrame`

**Responsibilities:**
- Load Excel file via `pd.read_excel()`
- Validate required columns: Item, Category, Cost, Date, Notes, Month, MonthNum, Year
- Coerce types:
  - `Item`, `Category`, `Year` → string
  - `Cost` → numeric (handles comma-formatted strings)
  - `Date` → datetime
  - `Notes` → string (if present)
- Raises `FileNotFoundError` or `ValueError` on failure

#### **`src/utils/plots.py`** (901 lines)
Matplotlib visualization with Qt integration.

**Core Class: `InteractiveCanvas(FigureCanvasQTAgg)`**
- Unified hover tooltip system for all chart types
- `set_line_data()`, `set_bar_data()`, `set_pie_data()` configure hover behavior
- Annotation anchored to x-axis (axes fraction coords) for stability
- Auto-detects closest data point within threshold for hover activation

**Chart Functions:** (all return `InteractiveCanvas` ready for Qt layout)

1. **`monthly_trend_figure(df, title)`**
   - Resamples data to monthly totals (`'MS'` frequency)
   - Plots line chart with markers
   - Annotates each point with dollar amount
   - Draws horizontal average line with label
   - X-axis: DateFormatter '%b %Y'

2. **`rolling_average_figure(df, window=3, title)`**
   - Computes rolling mean and std (causal window)
   - Plots raw monthly points (gray) + rolling mean (blue)
   - Shaded volatility band (mean ± std)
   - Explanatory caption below chart

3. **`top_items_bar_chart(df, top_n=10, title)`**
   - Groups by item, sums costs, sorts descending
   - **Stacked horizontal bars:** each segment = one transaction
   - Segments colored by category using `get_category_color()`
   - Hover shows: Item — Category — Notes
   - Total amount annotated at bar end

4. **`category_pie_chart(df, top_n=10, title)`**
   - Groups by category, sums costs
   - Donut chart (wedgeprops width=0.38)
   - Optional: aggregate small categories into "Other"
   - Center text shows total amount
   - Colors from `get_category_color()`

5. **`amount_distribution_pie(df, title)`**
   - Uses `pd.qcut()` to create quartile bins (Q1-Q4)
   - Slices represent total spend in each quartile
   - Hover includes transaction count per quartile

6. **`monthly_pie_chart(monthly_series, title)`**
   - Accepts pandas Series (datetime index, numeric values)
   - Donut chart with month labels + amounts on wedges
   - Center total amount text

7. **`cumulative_spending_figure(df, title)`**
   - Shows day-by-day cumulative spending (running total)
   - Includes all days (even with $0 spending)
   - Line chart with final total annotation
   - Hover shows date and cumulative amount

#### **`src/utils/xlsx_handler.py`** (400 lines)
Excel file manipulation and formatting.

**Main Function: `remake_xlsx_file(xlsx_path)`**

**Workflow:**
1. **Backup Creation:** Timestamped copy (`purchases_backup_YYYY-MM-DD_HH-MM-SS.xlsx`)
2. **Column Initialization:** Ensures headers A-H exist via `xlsx_init_column()`
3. **Data Sorting:** Reads all rows, sorts by Date column (oldest → newest)
4. **Row Rewrite:** Clears existing rows, writes sorted data starting at row 2
5. **Validation & Formatting:**
   - `xlsx_create_category_dv()`: Creates dropdown list for Category column
   - `xlsx_create_category_cf()`: Conditional formatting based on category
   - `xlsx_format_rows()`: Applies borders, fills, number formats

**Helper Functions:**
- `xlsx_init_column(ws, col_letter, text, width)`: Sets header, font, alignment, width
- `xlsx_format_rows(ws, cols)`: Applies alternating month fills, subscription highlighting
- `xlsx_create_category_dv(ws, category_col)`: DataValidation with predefined categories
- `xlsx_create_category_cf(ws, category_col)`: FormulaRule-based conditional formatting

#### **`src/utils/xlsx_formats.py`** (48 lines)
Openpyxl style constants:

- **CATEGORIES:** List of 11 category names
- **FILL_MAP:** Dict mapping categories to PatternFill (hex colors)
- **FILL_WHITE, FILL_GREY, FILL_SUBSCRIPTION:** Predefined fills
- **BORDER_LEFT_RIGHT, BORDER_ALL:** Thin border styles
- **ALIGN_CENTER, ALIGN_LEFT:** Alignment objects
- **FONT_BOLD:** Bold font
- **FORMAT_MONEY, FORMAT_DATE:** Excel number format strings

#### **`src/utils/category_colors.py`** (36 lines)
Central color mapping for consistency across charts and Excel.

**`category_colors` dict:** 11 categories → hex colors
- Food & Beverages: #D9D9D9 (gray)
- Books & Literature: #e9a9ff (light purple)
- Gaming: #bbe33d (lime green)
- Digital Subscriptions: #fbffa9 (yellow)
- Movies & Media: #a05eff (purple)
- etc.

**`get_category_color(category: str) -> str`:**
- Returns hex color string
- Defensive: handles None, falls back to 'Miscellaneous' color
- Used by matplotlib plots and Excel conditional formatting

#### **`src/utils/path_helpers.py`** (15 lines)
PyInstaller-aware path resolution.

**`get_data_folder() -> Path`:**
- If `sys.frozen` (PyInstaller exe): Returns `Path(sys.executable).parent / 'data'`
- Otherwise: Returns repo-relative `Path(__file__).parent.parent / 'data'`
- Ensures packaged executables find the external `data/` folder

---

## Core Components Deep Dive

### Dashboard Page Architecture

**Initialization Flow:**
1. `_init_ui()`: Create scroll area, controls row (year combo, search box, buttons)
2. Create content widget inside scroll area
3. `_init_stats_section()`: 13 KPI cards in 3 rows (QFrame with QHBoxLayouts)
4. `_init_overall_data_section()`: Chart selector, placeholder for canvas/tables
5. `_init_monthly_details_section()`: Month pie, month combo, items table (initially hidden)
6. `_init_category_section()`: Category combo, placeholder for chart/table
7. `set_data()`: Load default data, populate year selector, trigger `_compute_and_update()`

**Filtering System:**
- **Year Filter:** Dropdown with "Last 12 months", "All" + detected years (newest first)
  - "Last 12 months" filters to show 12 complete calendar months (e.g., if latest date is Jan 2026, shows Feb 2025 - Jan 2026)
  - Years sorted in descending order (2026, 2025, etc.)
  - Connected to `_on_year_changed()` → `_compute_and_update()`
- **Search Filter:** Text input + explicit "Search" button
  - Filters Item and Notes columns (case-insensitive substring)
  - Connected to `_compute_and_update()` via button click

**Update Cascade:**
```
_compute_and_update(year_text)
  │
  ├─> Apply year filter to _data_raw
  ├─> Apply search filter to filtered DataFrame
  │
  ├─> _update_metrics(df_sel)
  │     └─> Calculate 13 KPIs, format as strings, update card labels + tooltips
  │
  ├─> _render_monthly_overview(df_sel)
  │     ├─> Clear existing canvases
  │     ├─> Create monthly_trend or rolling_average figure
  │     ├─> Create category_pie and amount_distribution pies (side-by-side)
  │     ├─> Create top_items_bar_chart
  │     └─> Populate top 10 most expensive table
  │
  ├─> _render_monthly_details(df_sel)  [only if year selected]
  │     ├─> Create monthly_pie_chart
  │     ├─> Populate month combo with 12 months
  │     ├─> Connect month combo to _populate_items_for(month_label)
  │     └─> Initially populate items table for first month
  │
  └─> _render_category_details(df_sel)
        ├─> Populate category combo with unique categories
        ├─> Filter by selected category
        ├─> Create category-specific top_items_bar_chart
        └─> Populate top 10 table for category
```

**Canvas Management:**
- `_clear_overall_canvases()`: Removes and deletes (`deleteLater()`) all matplotlib canvases
- Prevents memory leaks and duplicate widgets in layout
- Called at start of `_render_monthly_overview()` before creating new charts

### Table View Architecture

**Model-View-Proxy Pattern:**
```
QTableView (UI)
     │
     ▼
DataFrameFilterProxy (filtering)
     │
     ▼
DataFrameModel (pandas wrapper)
     │
     ▼
pandas DataFrame (data source)
```

**Sorting Implementation:**
1. User clicks column header
2. `QTableView` calls `proxy_model.sort(column, order)`
3. Proxy maps column index to source model column by header name
4. Proxy calls `source_model.sort(src_col, order)`
5. Source model sorts underlying DataFrame using `df.sort_values(by=colname, ascending=ascending, kind='mergesort')`
6. Model emits `beginResetModel()` / `endResetModel()`
7. View updates to show sorted data

**Why This Design:**
- pandas sorting handles numeric and datetime columns correctly (not lexicographic)
- Proxy layer adds substring filtering without modifying source data
- Separation of concerns: model owns data, proxy owns filtering/sorting logic

### Visualization System

**InteractiveCanvas Design Philosophy:**
- **Single Annotation:** One shared annotation object per canvas, repositioned on hover
- **Axes-Fraction Positioning:** Annotation anchored at `(x_frac, 0)` (x-axis)
  - Ensures tooltip stays visible regardless of zoom or pan
  - x_frac computed as `(data_x - xmin) / (xmax - xmin)` for line charts
  - Fixed at 0.5 (center) for bar/pie charts
- **Auto-Detection:** `on_hover()` dispatches to `_handle_line_hover()`, `_handle_bar_hover()`, or `_handle_pie_hover()` based on `chart_type`
- **Threshold Logic:**
  - Line charts: Within 5% of x-range or 30 days for datetime
  - Bar charts: `bar.contains(event)` check
  - Pie charts: `wedge.contains(event)` check

**Chart Annotation Strategy:**
- **Monthly Trend:** Each data point annotated with amount above marker
- **Rolling Average:** Caption below chart explaining rolling window
- **Bar Charts:** Total amount at end of each bar
- **Pie Charts:** Center text shows total, hover shows individual amounts + percentages

---

## Data Flow

### Loading Sequence

1. **User Opens App:**
   ```python
   main() → MainWindow.__init__() → DashboardPage displayed
   ```

2. **DashboardPage Initialization:**
   ```python
   __init__() → _init_ui() → set_data()
   ```

3. **Data Loading:**
   ```python
   set_data(df=None)
     │
     ├─> load_df("data/purchases.xlsx")  # via data_loader.py
     │     └─> pd.read_excel() + type coercion
     │
     ├─> Store as _data_raw
     │
     ├─> Extract unique years from 'Year' or 'Date' column
     │
     ├─> Populate year_combo dropdown:
     │   - "Last 12 months" (default selection)
     │   - "All"
     │   - Years in descending order (2026, 2025, ...)
     │
     └─> _compute_and_update("Last 12 months")
           └─> [see Update Cascade above]
   ```

### Filtering & Search Flow

**Year Selection:**
```
User selects year/period → year_combo.currentTextChanged
  │
  └─> _on_year_changed(text)
        └─> _compute_and_update(text)
              ├─> Filter _data_raw by:
              │   - 'Last 12 months': 12 complete calendar months (current month + 11 prior)
              │   - 'All': no filter
              │   - Year (e.g., '2026'): filter by specific year
              └─> [Update Cascade]
```

**Search Button:**
```
User enters text + clicks Search → _search_button.clicked
  │
  └─> lambda: _compute_and_update(year_combo.currentText())
        ├─> Filter by year
        ├─> Apply search filter (Item or Notes contains text)
        └─> [Update Cascade]
```

### Excel Remake Flow

```
User clicks "Remake purchases.xlsx" → _on_remake_clicked()
  │
  ├─> Show confirmation dialog
  │
  ├─> Get purchases_path from main_window.data_dir
  │
  └─> remake_xlsx_file(purchases_path)
        │
        ├─> Load workbook with openpyxl
        │
        ├─> Create timestamped backup
        │
        ├─> Initialize columns A-H (headers + widths)
        │
        ├─> Read all data rows
        │
        ├─> Sort rows by Date column (oldest → newest)
        │
        ├─> Clear existing rows 2+
        │
        ├─> Write sorted rows back
        │
        ├─> Apply data validation (Category dropdown)
        │
        ├─> Apply conditional formatting (category colors)
        │
        ├─> Apply row formatting (borders, fills, number formats)
        │
        └─> Save workbook
```

---

## Key Features Implementation

### 1. Dynamic KPI Calculation

**Location:** `dashboard.py` → `_update_metrics(df)`

**Process:**
1. Convert Cost to numeric, fill NaN with 0.0
2. Resample by month/week/year using `df.set_index('Date')['Cost'].resample(...)`
3. Compute statistics:
   - Total: `costs.sum()`
   - Average: `costs.mean()`
   - Quartiles: `costs.quantile(0.25/0.5/0.75)`
   - Volatility: `monthly.std()`
4. Format values using helper functions (`_fmt_money`, `_fmt_num`)
5. Update QLabel widgets in `_cards` dict
6. Set tooltips with plain-language explanations

**Example Tooltip:**
```
"Spending volatility": "How much your monthly spending goes up and down. 
Higher means spending swings more from month to month."
```

### 2. Chart Selector (Monthly Trend vs Rolling Average)

**Location:** `dashboard.py` → `_init_overall_data_section()`

**Implementation:**
- QComboBox with 2 items: "Monthly spending trend", "Rolling average"
- Connected to `_on_overview_chart_changed()`:
  ```python
  def _on_overview_chart_changed(self):
      df_sel = getattr(self, '_data', self._data_raw)
      self._render_monthly_overview(df_sel)
  ```
- `_render_monthly_overview()` checks `_overview_chart_combo.currentText()`:
  ```python
  if sel == 'Rolling average':
      self._monthly_view = rolling_average_figure(df_sel, title=f"3-month rolling average")
  else:
      self._monthly_view = monthly_trend_figure(df_sel, title="Monthly Spending Trend")
  ```

### 3. Stacked Category-Colored Bar Charts

**Location:** `plots.py` → `top_items_bar_chart()`

**Algorithm:**
1. Group by item, sum costs, take top N
2. For each top item, extract individual transactions from df
3. Plot horizontal bars where each segment = one transaction:
   ```python
   for seg_val in transaction_segments:
       category = get_category_from_transaction(seg_val)
       color = get_category_color(category)
       ax.barh(y, seg_val, left=cumulative_left, color=color, edgecolor='white')
       cumulative_left += seg_val
   ```
4. Annotate total at bar end
5. Hover shows: Item — Category — Notes

**Why Stacked:** Visualizes purchase frequency + category breakdown in one chart

### 4. Month Pie Chart with 12 Months

**Location:** `dashboard.py` → `_render_monthly_details()`

**Key Logic:**
```python
# Infer year from filtered data
years_in_data = pd.DatetimeIndex(df['Date'].dropna()).year.unique()
if len(years_in_data) == 1:
    inferred_year = int(years_in_data[0])
    months = pd.date_range(start=f"{inferred_year}-01-01", periods=12, freq='MS')

# Resample and reindex to ensure all 12 months present
monthly = df.set_index('Date')['Cost'].resample('MS').sum()
monthly = monthly.reindex(months, fill_value=0.0)
```

**Result:** Always shows 12 slices for a single year, even if some months have $0.00

### 5. Remake XLSX with Date Sorting

**Location:** `xlsx_handler.py` → `remake_xlsx_file()`

**Sorting Implementation:**
```python
def _parse_date(val):
    if isinstance(val, (datetime.datetime, datetime.date)):
        return datetime.datetime(val.year, val.month, val.day)
    return datetime.datetime.fromisoformat(str(val))

sortable = []
for row in data_rows:
    parsed = _parse_date(row[date_col_index])
    if parsed:
        row_copy[date_col_index] = parsed  # Replace with datetime object
        sortable.append((parsed, row_copy))

sortable.sort(key=lambda x: x[0])  # Sort by datetime
sorted_rows = [r for _, r in sortable] + nonsortable
```

**Why Datetime Replacement:** Ensures Excel interprets cells as dates, not strings

---

## UI Framework & Design

### PySide6 / Qt Architecture

**Window Structure:**
```
MainWindow (QMainWindow)
  ├─ Menu Bar (File, Help)
  ├─ Central Widget → DashboardPage
  └─ Status Bar
```

**No Navigation:**
- App directly displays dashboard
- No sidebar or page switching
- Single-page application focused on spending analysis

**Scrolling Strategy:**
- Dashboard uses `QScrollArea` with `widgetResizable=True`
- Content widget inside scroll area has `QVBoxLayout` with `Qt.AlignTop`
- Controls (year selector, search) fixed at top (outside scroll area)
- Allows vertical scrolling while keeping controls visible

### Layout Patterns

**Dashboard Section Structure:**
```python
section_frame = QFrame()
section_frame.setFrameShape(QFrame.StyledPanel)
section_layout = QVBoxLayout(section_frame)

header = QLabel("<b>Section Title</b>")
section_layout.addWidget(header)

# Content area (matplotlib canvas or tables)
canvas = monthly_trend_figure(df)
section_layout.addWidget(canvas)
```

**KPI Cards Pattern:**
```python
card = QFrame()
card.setFrameShape(QFrame.StyledPanel)
card_layout = QVBoxLayout(card)
title = QLabel("<b>Metric Name</b>")
value_label = QLabel("—")
value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
card_layout.addWidget(title)
card_layout.addWidget(value_label)
```

### Matplotlib Embedding

**Integration Steps:**
1. Create `Figure` object: `fig = Figure(figsize=(10, 4), dpi=100)`
2. Create `InteractiveCanvas(fig)` (inherits `FigureCanvasQTAgg`)
3. Add subplot: `ax = fig.add_subplot(111)`
4. Plot data using matplotlib API
5. Call `fig.tight_layout()` before returning
6. Add canvas to Qt layout: `layout.addWidget(canvas)`

**Memory Management:**
- Always call `deleteLater()` on old canvases before creating new ones
- Use `layout.removeWidget(canvas)` before deletion
- Store canvas references as instance variables for cleanup

---

## Excel File Management

### Expected File Structure

**Required Columns (case-sensitive):**
| Column    | Type       | Description                      |
|-----------|------------|----------------------------------|
| Item      | String     | Purchase description             |
| Category  | String     | One of 11 predefined categories  |
| Cost      | Numeric    | Amount spent (supports commas)   |
| Date      | Datetime   | Purchase date                    |
| Notes     | String     | Optional notes                   |
| Month     | String     | Month name (auto-filled)         |
| MonthNum  | Integer    | Month number 1-12 (auto-filled)  |
| Year      | String     | Year (auto-filled)               |

**Column Layout (A-H):**
- A: Item (width 15)
- B: Category (width 15) [dropdown validation]
- C: Cost (width 10) [money format]
- D: Date (width 12) [date format dd/mm/yyyy]
- E: Notes (width 15)
- F: Month (width 12) [auto-calculated]
- G: MonthNum (width 5) [auto-calculated]
- H: Year (width 10) [auto-calculated]

### Formatting Rules

**Row Fills:**
- Even months: White (#FFFFFF)
- Odd months: Gray (#D9D9D9)
- Digital Subscriptions category: Yellow (#fbffa9) (overrides month fill)

**Category Conditional Formatting:**
- Each category in `FILL_MAP` gets a FormulaRule
- Formula: `$B2="Category Name"` (locked column, relative row)
- Applies category-specific color to entire row

**Borders:**
- Header row: All borders (top, bottom, left, right)
- Data rows: Left and right borders only (for cleaner look)

**Number Formats:**
- Cost: `"$"* #,##0.00` (currency with thousands separator)
- Date: `dd/mm/yyyy`

**Data Validation:**
- Category column (B) has dropdown list with 11 categories
- Applies to rows 2 through `max_row*2` (accommodates growth)
- `allow_blank=True` for flexibility

### Backup Strategy

**Filename Pattern:** `purchases_backup_YYYY-MM-DD_HH-MM-SS.xlsx`

**Backup Timing:** Before any modifications in `remake_xlsx_file()`

**Storage:** Same folder as original file

**Why Timestamped:** Allows multiple backups without overwriting, easy to identify latest

---

## Visualization System

### Color Scheme

**Category Colors (from `category_colors.py`):**
```python
{
    'Food & Beverages': '#D9D9D9',         # Gray
    'Books & Literature': '#e9a9ff',       # Light purple
    'Gaming': '#bbe33d',                   # Lime green
    'Digital Subscriptions': '#fbffa9',    # Yellow
    'Movies & Media': '#a05eff',           # Purple
    'Music & Audio': '#ffa9f2',            # Pink
    'Electronics & Accessories': '#729fcf',# Blue
    'Clothing & Apparel': '#D9D9D9',       # Gray
    'Health & Personal Care': '#a9ffc4',   # Mint green
    'Collectibles': '#ffc85d',             # Orange
    'Miscellaneous': '#D9D9D9'             # Gray (fallback)
}
```

**Why These Colors:**
- High contrast for accessibility
- Distinct hues for easy visual differentiation
- Gray used for generic/uninteresting categories
- Vibrant colors for key spending areas (Gaming, Movies, etc.)

### Chart Types & Use Cases

**1. Monthly Trend (Line Chart)**
- **Purpose:** Show spending trajectory over time
- **Best For:** Identifying seasonal patterns, growth trends
- **Annotations:** Each point labeled with amount, average line overlaid

**2. Rolling Average (Line Chart + Band)**
- **Purpose:** Smooth out month-to-month volatility
- **Best For:** Understanding underlying spending trend
- **Annotations:** Caption explaining 3-month window, volatility band

**3. Top Items (Horizontal Bar Chart)**
- **Purpose:** Identify highest-spend items
- **Best For:** Finding budget outliers, understanding purchase frequency
- **Annotations:** Total at bar end, hover shows individual transactions

**4. Category Pie (Donut Chart)**
- **Purpose:** Budget allocation by category
- **Best For:** High-level spending breakdown
- **Annotations:** Center total, hover shows amount + percentage

**5. Amount Distribution Pie (Donut Chart)**
- **Purpose:** Understand spending by transaction size (quartiles)
- **Best For:** Identifying small vs large purchases
- **Annotations:** Center total, hover shows count + amount

**6. Monthly Pie (Donut Chart)**
- **Purpose:** Compare spending across 12 months
- **Best For:** Yearly budget review, seasonal analysis
- **Annotations:** Month labels on wedges, hover shows details

### Hover Tooltip Design

**Positioning Strategy:**
- Annotation anchored at `(x_frac, 0)` using axes fraction coordinates
- `y=0` places tooltip at x-axis level (bottom of plot)
- `xytext=(0, 10)` offsets 10 points above x-axis
- `ha='center'` centers text horizontally

**Benefits:**
- Always visible (won't go off-screen)
- Doesn't obscure data points
- Consistent behavior across zoom/pan

**Formatting:**
- White background, gray border (`bbox=dict(boxstyle='round', fc='w', alpha=0.95, edgecolor='gray')`)
- Fontsize 10 for readability
- zorder=1000 ensures tooltip always on top

---

## Development Guide

### Setting Up Development Environment

**1. Clone Repository:**
```powershell
git clone https://github.com/dragonstonehafiz/budgeting-analysis.git
cd budgeting-analysis
```

**2. Create Virtual Environment:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies:**
```powershell
pip install -r requirements.txt
```

**4. Prepare Data Folder:**
- Create `data/` directory in project root
- Place `purchases.xlsx` inside (or use "Remake" button to initialize)

**5. Run Application:**
```powershell
python src/qt_app.py
```

### Building Executable

**Using PyInstaller:**
```powershell
pyinstaller --noconfirm --clean --name "BudgetingApp" --onefile --windowed src/qt_app.py
```

**Output:** `dist/BudgetingApp.exe`

**Important:** Place `data/` folder next to the executable (not inside `dist/`)

**Why `--windowed`:** Suppresses console window (Qt apps should be GUI-only)

### Adding a New Chart Type

**Step 1: Implement in `plots.py`**
```python
def my_new_chart(df: pd.DataFrame, title: str = None):
    fig = Figure(figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)
    
    # ... plot data using ax.plot(), ax.bar(), etc. ...
    
    # Set up hover data
    canvas.set_line_data(x_data, y_data, ax, line)
    
    fig.tight_layout()
    return canvas
```

**Step 2: Add to Dashboard**
```python
# In dashboard.py, _render_monthly_overview() or similar
self._new_chart_view = my_new_chart(df_sel, title="My Chart")
self.some_section.content.layout().addWidget(self._new_chart_view)
```

**Step 3: Clean Up on Re-render**
```python
# In _clear_overall_canvases() or similar
nc = getattr(self, '_new_chart_view', None)
if nc is not None:
    layout.removeWidget(nc)
    nc.deleteLater()
    self._new_chart_view = None
```

### Adding a New KPI

**Step 1: Update `_update_metrics()` in `dashboard.py`**
```python
# Calculate new metric
new_metric = float(costs.some_calculation())

# Add to mapping dict
mapping['New Metric'] = _fmt_money(new_metric)

# Add tooltip
tooltips['New Metric'] = 'Plain-language explanation of metric.'
```

**Step 2: Add Card in `_init_stats_section()`**
```python
row4 = ('New Metric', 'Other Metric')
self._create_cards_row(stats_layout, row4)
```

### Adding a New Category

**Step 1: Update `xlsx_formats.py`**
```python
CATEGORIES = [
    # ... existing categories ...
    "New Category"
]

FILL_MAP = {
    # ... existing mappings ...
    "New Category": PatternFill(fgColor="abcdef", fill_type="solid")
}
```

**Step 2: Update `category_colors.py`**
```python
category_colors = {
    # ... existing colors ...
    'New Category': '#abcdef'
}
```

**Step 3: Remake Excel File**
- Run app, click "Remake purchases.xlsx"
- Dropdown will now include new category

---

## Common Patterns & Conventions

### Error Handling

**Defensive Programming:**
- Wrap all DataFrame operations in try-except
- Use `errors='coerce'` for type coercion (returns NaN instead of raising)
- Check for None/empty DataFrames before processing
- Log exceptions with `logger.exception()` but don't crash UI

**Example:**
```python
try:
    df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce').fillna(0.0)
except Exception:
    df['Cost'] = 0.0  # Fallback
```

### Signal Handling

**Disconnect Before Reconnect:**
```python
try:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        self.year_combo.currentTextChanged.disconnect()
except Exception:
    pass
self.year_combo.currentTextChanged.connect(self._on_year_changed)
```

**Why:** Prevents duplicate connections if `set_data()` called multiple times

**BlockSignals for Programmatic Changes:**
```python
self.year_combo.blockSignals(True)
self.year_combo.clear()
self.year_combo.addItems(years)
self.year_combo.blockSignals(False)
```

**Why:** Avoid triggering handlers during initialization

### Type Coercion

**Standard Pattern:**
```python
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df = df.dropna(subset=[date_col])  # Remove invalid dates

df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)
```

**Why `errors='coerce'`:** Converts invalid values to NaT/NaN instead of raising exceptions

**Why `fillna(0.0)`:** Ensures numeric operations don't fail on NaN

### Layout Insertion

**Insert at Specific Index:**
```python
# Insert chart after controls (index 1) but before tables
self.section.content.layout().insertWidget(1, canvas)
```

**Why Not Always Append:** Maintains visual order when re-rendering

**Remove Before Adding:**
```python
if self._canvas is not None:
    layout.removeWidget(self._canvas)
    self._canvas.deleteLater()
self._canvas = new_canvas
layout.insertWidget(index, self._canvas)
```

### Formatting Helpers

**Money Formatting:**
```python
def _fmt_money(x):
    try:
        return f"${x:,.2f}"
    except Exception:
        return str(x)
```

**Number Formatting:**
```python
def _fmt_num(x):
    try:
        if isinstance(x, float) and x.is_integer():
            return str(int(x))
        return f"{x:,}"
    except Exception:
        return str(x)
```

**Date Formatting:**
```python
date_str = pd.to_datetime(date_val).strftime('%Y-%m-%d') if pd.notna(date_val) else str(date_val)
```

---

## Testing & Debugging

### Common Issues

**Issue 1: "Missing required columns" error**
- **Cause:** Excel file doesn't have expected headers
- **Solution:** Use "Remake purchases.xlsx" button to initialize columns

**Issue 2: Charts not updating after filter**
- **Cause:** `_data` not updated in `_compute_and_update()`
- **Solution:** Ensure `self._data = df_sel` before calling render functions

**Issue 3: Tooltips not showing**
- **Cause:** `set_*_data()` not called on canvas, or data empty
- **Solution:** Verify chart_data populated, check console for exceptions

**Issue 4: Memory leak / app slowdown**
- **Cause:** Old matplotlib figures not cleaned up
- **Solution:** Call `deleteLater()` on canvases before creating new ones

**Issue 5: Executable can't find data folder**
- **Cause:** `get_data_folder()` not handling frozen state
- **Solution:** Verify `sys.frozen` check, place `data/` next to .exe

### Logging

**Current Implementation:**
```python
import logging
logger = logging.getLogger(__name__)

logger.exception("Failed rendering monthly overview")
```

**To Enable Console Logging:**
```python
# Add to qt_app.py main() before creating MainWindow
logging.basicConfig(level=logging.DEBUG)
```

### Validation Checks

**Data Integrity:**
```python
# After loading DataFrame
assert 'Date' in df.columns, "Date column missing"
assert df['Date'].notna().any(), "No valid dates"
assert df['Cost'].sum() > 0, "No spend data"
```

**UI State:**
```python
# Before rendering
if not hasattr(self, '_data') or self._data is None:
    return
if self._data.empty:
    return
```

---

## Performance Considerations

### Optimization Strategies

**1. Avoid Repeated DataFrame Copies**
```python
# BAD: creates new DataFrame each time
for _ in range(100):
    df_copy = df.copy()
    
# GOOD: copy once, reuse
df_copy = df.copy()
for _ in range(100):
    process(df_copy)
```

**2. Use Vectorized Operations**
```python
# BAD: iterrows() is slow
for idx, row in df.iterrows():
    df.at[idx, 'Year'] = row['Date'].year
    
# GOOD: vectorized assignment
df['Year'] = df['Date'].dt.year
```

**3. Resample Instead of GroupBy for Time Series**
```python
# GOOD: built-in time-aware grouping
monthly = df.set_index('Date')['Cost'].resample('MS').sum()
```

**4. Limit DataFrame Size in Memory**
```python
# Only load necessary columns
df = pd.read_excel(path, usecols=['Item', 'Cost', 'Date'])
```

### UI Responsiveness

**Use QApplication.processEvents() for Long Operations:**
```python
for i in range(1000):
    # ... heavy computation ...
    if i % 100 == 0:
        QApplication.processEvents()  # Keep UI responsive
```

**Defer Heavy Rendering:**
```python
# Don't render all charts at once
QTimer.singleShot(100, lambda: self._render_category_details(df))
```

---

## Roadmap & Future Enhancements

### Potential Features

**1. Budget Goals & Alerts**
- Set monthly/category spending limits
- Visual indicators when approaching/exceeding budget

**2. Export Reports**
- Generate PDF summaries with charts
- CSV export of filtered data

**3. Multi-File Support**
- Load multiple Excel files (e.g., different years)
- Merge and analyze across files

**4. Advanced Filtering**
- Date range picker (custom start/end dates)
- Multi-category selection
- Amount range filters

**5. Custom Categories**
- User-defined category list (not hardcoded)
- Import/export category configurations

**6. Undo/Redo for Excel Edits**
- Restore previous versions from backups
- Built-in backup browser

**7. Dark Mode**
- Qt stylesheet for dark theme
- Matplotlib style configuration

### Known Limitations

**1. Single Worksheet:**
- Only processes first sheet in Excel file
- No support for multi-sheet workbooks

**2. Fixed Column Layout:**
- Expects columns A-H in specific order
- Adding custom columns breaks "Remake" function

**3. No Cloud Sync:**
- Data stored locally only
- No multi-device access

**4. Limited Currency Support:**
- Hardcoded to USD ($)
- No international currency formatting

**5. No Collaborative Editing:**
- Single-user application
- No merge conflict resolution

---

## Contributing Guidelines

### Code Style

**Follow PEP 8:**
- 4 spaces for indentation
- Max line length: 100 characters (flexible for readability)
- Two blank lines between top-level functions/classes

**Naming Conventions:**
- Classes: `UpperCamelCase`
- Functions/methods: `snake_case`
- Private methods: `_leading_underscore`
- Constants: `UPPER_CASE`

**Type Hints (Preferred):**
```python
def load_df(filepath: str | Path = "data/purchases.xlsx") -> pd.DataFrame:
    ...
```

**Docstrings (Google Style):**
```python
def my_function(arg1: str, arg2: int) -> bool:
    """Brief one-line description.
    
    More detailed explanation if needed.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When arg2 is negative.
    """
```

### Pull Request Process

**1. Create Feature Branch:**
```bash
git checkout -b feature/my-new-feature
```

**2. Make Changes:**
- Update code
- **Update this agents.md file** with new architecture/patterns
- Add tests if applicable

**3. Test Locally:**
```powershell
python src/qt_app.py  # Verify UI works
pyinstaller ...       # Test executable build
```

**4. Commit with Clear Message:**
```bash
git commit -m "feat: Add budget goal alerts with visual indicators"
```

**5. Push and Open PR:**
```bash
git push origin feature/my-new-feature
```

### What to Document in agents.md

**When Adding New Files:**
- File purpose and responsibilities
- Key classes/functions with signatures
- Integration points with existing code

**When Changing Architecture:**
- Update flow diagrams
- Revise data flow descriptions
- Document breaking changes

**When Adding Dependencies:**
- Update requirements.txt
- Document new library usage in relevant sections
- Explain why library was chosen

---

## Appendix: Quick Reference

### File Locations Cheat Sheet
```
src/
  qt_app.py             → Main entry, navigation
  pages/
    dashboard.py        → Analytics + KPIs + charts
    table_view.py       → Sortable table view
  utils/
    data_loader.py      → Excel → DataFrame
    plots.py            → Matplotlib charts
    xlsx_handler.py     → Excel write/format
    xlsx_formats.py     → Openpyxl constants
    category_colors.py  → Color mapping
    path_helpers.py     → PyInstaller paths
```

### Key Classes
```
MainWindow              → App window, menu bar
DashboardPage           → Dashboard UI, KPIs, charts
InteractiveCanvas       → Matplotlib canvas with hover
```

### Key Functions
```
load_df(path)                     → Load Excel to DataFrame
remake_xlsx_file(path)            → Backup, sort, format Excel
monthly_trend_figure(df)          → Line chart canvas
top_items_bar_chart(df)           → Stacked bar canvas
category_pie_chart(df)            → Donut pie canvas
get_category_color(category)      → Hex color string
get_data_folder()                 → PyInstaller-aware data path
```

### Signal Connections Cheat Sheet
```
year_combo.currentTextChanged     → _on_year_changed
_search_button.clicked            → _compute_and_update
_remake_btn.clicked               → _on_remake_clicked
_overview_chart_combo.currentText → _on_overview_chart_changed
_month_combo.currentTextChanged   → _populate_items_for
_category_combo.currentTextChanged→ _render_category_details
```

---

**Last Updated:** [Update this date when modifying the file]  
**Maintained By:** AI Agents working on this repository  
**License:** Same as project license

**Remember:** Keep this file in sync with code changes! 🤖
