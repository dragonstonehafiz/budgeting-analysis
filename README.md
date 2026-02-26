# Budgeting Analysis

A personal spending dashboard built as a web app. The backend exposes a FastAPI REST API that reads from a local `.xlsx` file; the frontend is a Vue 3 + Vite SPA that visualises the data with interactive charts.

## Features

- **Year & search filtering** — filter transactions by year or free-text search (Item / Notes)
- **Tag filtering** — multi-select tag filter with OR matching
- **Category charts** — donut, horizontal bar, and line charts
- **Store icons** — normalised store-name to icon mapping shown in the Settings page
- **XLSX remake** — reformat and sort the source spreadsheet in one click, with automatic backup

## Tech Stack

| Layer    | Technologies                       |
| -------- | ---------------------------------- |
| Backend  | Python, FastAPI, pandas, openpyxl  |
| Frontend | Vue 3, Vite, Chart.js, vue-chartjs |
| Data     | `backend/data/purchases.xlsx`      |

## Data Format

Place your data file at `backend/data/purchases.xlsx`. The workbook must have a sheet with the following columns in this exact order (column names are case-sensitive):

| Column     | Type    | Description                                              |
| ---------- | ------- | -------------------------------------------------------- |
| `ID`       | integer | Unique row identifier                                    |
| `Item`     | string  | Name or description of the purchase                      |
| `Category` | string  | Spending category (e.g. Groceries, Transport)            |
| `Cost`     | number  | Purchase amount                                          |
| `Date`     | date    | Date of purchase — must be a proper Excel date value     |
| `Store`    | string  | Store or vendor name                                     |
| `Tags`     | string  | Comma-separated tags (e.g. `essential,recurring`)        |
| `Notes`    | string  | Optional free-text notes                                 |

Once your data is in place, use the **Remake XLSX** button in the app to apply formatting, sort rows by date, and create a timestamped backup. The file must already contain the columns above for this to work.

## Running Locally (Dev)

**Backend**

```powershell
cd backend
.venv\Scripts\activate
python server.py
```

Runs on `http://localhost:8000`.

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. API calls are proxied to the backend via Vite's dev proxy.

## Running with Docker

```bash
docker compose up --build
```

| Service  | Host URL              |
| -------- | --------------------- |
| Frontend | http://localhost:5173 |
| Backend  | http://localhost:8000 |

`backend/data/` is mounted as a volume so the XLSX file persists across container rebuilds.
