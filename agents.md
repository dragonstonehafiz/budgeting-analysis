# agents.md — Budgeting Analysis Web App

> **⚠️ IMPORTANT INSTRUCTION FOR AI AGENTS:**
>
> **This file MUST be updated whenever code changes are made to this project.**
> - When modifying any source files, update the relevant sections below
> - When adding new features, document them in the appropriate sections
> - Keep code examples in sync with actual implementation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Frontend Architecture](#frontend-architecture)
4. [Pages](#pages)
5. [Shared Components](#shared-components)
6. [Chart Components](#chart-components)
7. [Data Composable — useChartData.js](#data-composable--usechartdatajs)
8. [Adding a New Chart](#adding-a-new-chart)

---

## Project Overview

A personal budgeting dashboard being migrated from a PySide6 desktop app to a
**FastAPI + Vue 3** web application running in Docker. The frontend is a Vue 3 + Vite
SPA using ApexCharts for all visualisations. The backend (in progress) will be a
FastAPI server that reads `data/purchases.xlsx` via pandas and serves JSON.

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite 7, Chart.js, vue-chartjs, chartjs-adapter-date-fns |
| Backend | FastAPI, pandas, openpyxl (running on port 8000) |
| Containerisation (planned) | Docker Compose |

### Data Shape

Raw transaction objects (as returned by `GET /transactions/`):
```js
{
  Date:     '2025-01-03',          // ISO date string
  Cost:     12.50,                 // number
  Category: 'Food & Beverages',   // string — see CATEGORY_COLORS for valid values
  Item:     'Groceries',          // string
  Month:    'January',            // string
  MonthNum: 1,                    // 1–12, used for chronological sort
  Notes:    '',                   // optional string
}
```

---

## Repository Structure

```
budgeting-analysis/
├── backend/                  # Python side (FastAPI + original PySide6 code)
│   ├── src/
│   │   ├── qt_app.py         # Original PySide6 entry point (legacy)
│   │   ├── pages/
│   │   └── utils/
│   │       ├── data_loader.py
│   │       ├── plots.py      # Matplotlib charts being replaced by Vue
│   │       ├── category_colors.py
│   │       ├── xlsx_handler.py
│   │       └── xlsx_formats.py
│   ├── data/                 # purchases.xlsx lives here (volume-mounted in Docker)
│   ├── images/
│   └── requirements.txt
├── frontend/                 # Vue 3 + Vite SPA
│   ├── src/
│   │   ├── main.js           # App entry — registers vue-router
│   │   ├── App.vue           # Router shell: <NavBar /> + <KeepAlive><RouterView /></KeepAlive>
│   │   ├── style.css         # Global reset / base styles
│   │   ├── router/
│   │   │   └── index.js      # vue-router config (/ → Home, /category → Category)
│   │   ├── pages/
│   │   │   ├── HomePage.vue      # KPI stats + line chart switcher + top items
│   │   │   └── CategoryPage.vue  # Category donut + drill-down bar chart + table
│   │   ├── components/
│   │   │   ├── FilterBar.vue        # Shared year-dropdown + optional search bar
│   │   │   ├── NavBar.vue           # Sticky top navigation bar
│   │   │   ├── StatCard.vue      # Reusable KPI stat card
│   │   │   └── charts/
│   │   │       ├── LineChart.vue
│   │   │       ├── DonutChart.vue
│   │   │       └── HorizontalBarChart.vue
│   │   └── composables/
│   │       ├── useGlobalFilters.js  # Singleton year/search/transactions state
│   │       └── useChartData.js      # All data transformation helpers + computeStats
│   ├── index.html
│   └── package.json
├── README.md
└── agents.md                 # This file
```

---

## Frontend Architecture

### Key Principles

1. **Display components are dumb.** `LineChart`, `DonutChart`, and `HorizontalBarChart`
   only render what they are given. They never fetch data or transform it.

2. **Data shaping happens in `useChartData.js`.** All grouping, bucketing, transposing,
   and color lookups live here. When the FastAPI backend is ready, these functions will
   be replaced by API calls, but the component interfaces stay the same.

3. **Colors live on data, not in components.** Category colors are resolved in the
   composable and passed into components as props. Components never hardcode colors.

### Global Registration

`vue-router` is registered globally in `main.js`:
```js
import router from './router'
app.use(router)
```

### Shared Filter State — `useGlobalFilters.js`
`frontend/src/composables/useGlobalFilters.js`

All year/search/transaction state lives as **module-level refs** in this composable.
Because ES modules are singletons, the refs persist for the entire browser session with no extra store needed.
Both pages import from it — changing the year on one page is instantly reflected on the other.

```js
const { availableYears, selectedYear, search, transactions, loading, initFilters } = useGlobalFilters()
onMounted(() => initFilters())
```

| Export | Type | Description |
|--------|------|-------------|
| `availableYears` | `Ref<string[]>` | `['All', '2025', ...]` — fetched once from `/api/transactions/years` |
| `selectedYear` | `Ref<string>` | Currently selected year; changing it auto-refetches transactions |
| `search` | `Ref<string>` | Free-text search string (used by HomePage, persists on nav) |
| `transactions` | `Ref<object[]>` | Year-filtered transactions from backend |
| `loading` | `Ref<boolean>` | True while a fetch is in flight |
| `initFilters()` | `async fn` | Call in `onMounted`; fetches years once and transactions if not yet loaded |

A `watch(selectedYear, ...)` inside the composable re-fetches transactions whenever the year changes, regardless of which page triggered the change.
The Vite dev proxy rewrites `/api/*` → `http://localhost:8000/*`. Year filtering is done server-side.
Search filtering (HomePage) is applied client-side over `transactions.value`.

---

## Pages

### HomePage.vue
`frontend/src/pages/HomePage.vue`  Route: `/`

Controls at top: **Year** dropdown (`All` + years desc from backend) + free-text **search** (filters by Item or Category).
All charts and stats derive from `transactions` (fetched from backend, year-filtered server-side) with search applied client-side.

**KPI rows**
- Row 1 (2 cards): Total Spent, Items Bought
- Row 2 (5 cards): Average Spend, Lower 25th Pctile, Median Spend, Upper 75th Pctile, Std Deviation
- Row 3 (4 cards): Avg Weekly Spend, Avg Monthly Spend, Avg Yearly Spend, Spending Volatility

**Chart switcher** — three `LineChart` instances toggled by buttons:
- Monthly Trend (`toSpendingSeries`)
- Cumulative (`toCumulativeSeries`)
- By Category (`toCategorySpendingSeries`) — one line per category, colored by `CATEGORY_COLORS`, legend shown
  
Bucket-size buttons (1-day / 7-day / 28-day) sit beside the switcher and drive all three charts.

**Bottom sections:** `HorizontalBarChart` (top 10 items) + sortable top-10 transactions table.

---

### CategoryPage.vue
`frontend/src/pages/CategoryPage.vue`  Route: `/category`

Controls at top: **Year** toggle buttons.

**Section 1 — Overview donut:** `DonutChart` showing spending by category for the selected year
(`topN=0`, `showLegend=true`).

**Section 2 — Drill-down:** Category `<select>` dropdown.
When a specific category is selected, shows:
- `HorizontalBarChart` — top 10 items in that category
- Top-10 transactions table for that category

---

## Shared Components

### FilterBar.vue
`frontend/src/components/FilterBar.vue`

Shared controls bar used at the top of every page. Reads directly from `useGlobalFilters` — no props needed for data.

**Props**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `showSearch` | Boolean | `false` | Show the free-text search input (used by HomePage only) |

**Usage**
```vue
<!-- CategoryPage -->
<FilterBar />

<!-- HomePage -->
<FilterBar :showSearch="true" />
```

---

### NavBar.vue
`frontend/src/components/NavBar.vue`

Sticky dark navbar (`#1a1a2e`) with lime `#bbe33d` accent. Two `RouterLink` targets: Home and Categories.
Uses `active-class="nav-link--active"` for highlighted current route.

---

### StatCard.vue
`frontend/src/components/StatCard.vue`

Reusable KPI display card.

**Props**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | String | required | Card heading |
| `value` | Number | required | Numeric value to display |
| `format` | String | `'currency'` | `'currency'` \| `'integer'` \| `'percent'` \| `'currency-rate'` |

**Usage**
```vue
<StatCard label="Total Spent"        :value="stats.totalSpent"  format="currency" />
<StatCard label="Items Bought"        :value="stats.itemsBought" format="integer" />
<StatCard label="Spending Volatility" :value="stats.volatility"  format="percent" />
```

---

## Chart Components

### LineChart.vue
`frontend/src/components/charts/LineChart.vue`

Generic time-series chart. Supports line, scatter, and rangeArea series in any combination
on the same chart — ApexCharts determines render type from each series object's `type` field.

**Props**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `series` | Array | required | Chart.js series array. Each item: `{ name, data: [{x,y}], type?, color? }`. `type` may be `'scatter'` or `'rangeArea'`; omit for a plain line. `color` sets the line/point color. |
| `title` | String | `''` | Chart subtitle shown inside the chart area |
| `averageLine` | Number | — | If provided, draws a dashed red horizontal annotation at this Y value |
| `caption` | String | `''` | Small grey text shown below the chart |
| `height` | Number | `320` | Chart height in px |
| `showLegend` | Boolean | `false` | Show the Chart.js legend above the chart |

**X-axis:** `type: 'datetime'`, formatted as `MMM 'yy`.
**Y-axis:** Dollar formatted (`$1,234`).

**Usage**
```vue
<LineChart
  :series="spendingSeries"
  :averageLine="154.82"
  title="Monthly Spending"
/>
```

**Series shapes accepted**
```js
// Plain line
{ name: 'Spending', data: [{ x: timestampMs, y: 120.50 }, ...] }

// Scatter
{ name: 'Raw', type: 'scatter', data: [{ x: timestampMs, y: 95.00 }, ...] }

// Range area (volatility band)
{ name: 'Band', type: 'rangeArea', data: [{ x: timestampMs, y: [low, high] }, ...] }
```

---

### DonutChart.vue
`frontend/src/components/charts/DonutChart.vue`

Donut chart with optional topN segment collapsing and optional right-side legend.
Center label always shows the total of **all** series (not just displayed segments).

**Props**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `series` | Array | required | Array of `{ label: string, value: number, color?: string }` |
| `title` | String | `''` | Heading above the chart |
| `topN` | Number | `10` | Show only the top N segments; remainder collapsed into grey "Other". Set `0` to show all. |
| `showLegend` | Boolean | `false` | Show the legend on the right side |
| `height` | Number | `380` | Chart height in px |

**Usage**
```vue
<DonutChart
  :series="categorySeries"
  title="Spending by Category"
  :topN="10"
  :showLegend="true"
/>
```

**Series shape**
```js
[
  { label: 'Gaming',             value: 570.00, color: '#bbe33d' },
  { label: 'Food & Beverages',   value: 312.50, color: '#D9D9D9' },
  // color is optional — falls back to a built-in palette if omitted
]
```

---

### HorizontalBarChart.vue
`frontend/src/components/charts/HorizontalBarChart.vue`

Stacked horizontal bar chart for top items by spend. Each bar represents one item;
each segment within a bar represents one individual purchase of that item.
Color is per-bar (derived from the item's dominant spending category), not per-segment.

**Props**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `series` | Array | required | Slot-major series from `toTopItemsSeries()` |
| `itemNames` | Array | required | Item name labels for the Y-axis, one per bar |
| `itemColors` | Array | required | One hex color per bar (by dominant category) |
| `title` | String | `''` | Heading above the chart |
| `showTotals` | Boolean | `false` | Show summed `$X.XX` label at the right end of each bar |
| `height` | Number | `400` | Chart height in px |

**Usage**
```vue
<HorizontalBarChart
  :series="topItems.series"
  :itemNames="topItems.itemNames"
  :itemColors="topItems.itemColors"
  title="Top 10 Items by Spend"
  :showTotals="true"
/>
```

**Why slot-major series?** ApexCharts stacked bar requires one series per "layer",
not one per bar. If Netflix was bought 4 times and Steam 2 times, the data is:
```js
series = [
  { name: 'Purchase 1', data: [15, 60] },   // 1st purchase of each item
  { name: 'Purchase 2', data: [15, 40] },   // 2nd purchase
  { name: 'Purchase 3', data: [15,  0] },   // Steam has no 3rd purchase → 0
  { name: 'Purchase 4', data: [15,  0] },
]
itemNames  = ['Netflix', 'Steam']
itemColors = ['#fbffa9', '#bbe33d']
```
`toTopItemsSeries()` performs this transposition automatically.

---

## Data Composable — useChartData.js
`frontend/src/composables/useChartData.js`

Plain JS utility module. All exports are pure functions — no Vue reactivity inside.

### Category Colors

```js
import { CATEGORY_COLORS, getCategoryColor } from './composables/useChartData.js'

getCategoryColor('Gaming')          // '#bbe33d'
getCategoryColor('Unknown')         // '#D9D9D9'  (Miscellaneous fallback)
```

`CATEGORY_COLORS` mirrors `backend/src/utils/category_colors.py`. Keep both in sync.

### Time-Series Helpers

| Function | Returns | Notes |
|----------|---------|-------|
| `bucketTransactions(txs, bucketDays)` | `[{x: ms, y: number}]` | Core bucketing primitive |
| `toSpendingSeries(txs, bucketDays=28)` | ApexCharts series array (1 series) | Spending trend |
| `toCumulativeSeries(txs, bucketDays=1)` | ApexCharts series array (1 series) | Running cumsum |
| `toCategorySpendingSeries(txs, bucketDays=28)` | Array of `{name, color, data}` series | One bucketed line per category, sorted by total spend desc |
| `computeAverage(txs, bucketDays=28)` | `number` | Scalar mean — used for `averageLine` prop |

### Donut Helpers

| Function | Returns |
|----------|---------|
| `toCategoryDonutSeries(txs)` | `[{label, value, color}]` sorted by value desc |
| `toMonthlyDonutSeries(txs)` | `[{label, value}]` sorted chronologically by MonthNum |

### Bar Chart Helper

```js
const { series, itemNames, itemColors } = toTopItemsSeries(transactions, topN = 10)
```
Groups by `Item`, sorts by total spend descending, picks top N, transposes into
slot-major series for ApexCharts. Item colors derived from the most-common Category
for each item.

### Stats Helper

```js
import { computeStats } from './composables/useChartData.js'

const stats = computeStats(transactions)
// stats.totalSpent        — sum of all costs
// stats.itemsBought       — transaction count
// stats.averageSpend      — mean cost per transaction
// stats.p25               — 25th percentile of individual transaction costs
// stats.median            — 50th percentile
// stats.p75               — 75th percentile
// stats.stdDev            — standard deviation of individual costs
// stats.avgWeeklySpend    — total / date-range-in-weeks
// stats.avgMonthlySpend   — average of monthly bucket totals
// stats.avgYearlySpend    — average of yearly bucket totals
// stats.spendingVolatility — coefficient of variation on monthly totals (%)
```

---

## Adding a New Chart

1. Create `frontend/src/components/charts/MyChart.vue`
   - Accept fully-shaped data via props — no fetching or transforming inside
   - Set `redrawOnParentResize: false` and `redrawOnWindowResize: false` to prevent jitter
   - Set `animations: { enabled: false }` for stability

2. Add a transform helper to `useChartData.js` if raw transactions need shaping

3. Import and use in the relevant page component (`HomePage.vue` or `CategoryPage.vue`)

4. Update this file
