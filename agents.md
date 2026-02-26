# AGENTS.md — Budgeting Analysis

Purpose: concise instructions for AI/code agents working in this repo.

## Scope
- Applies to the entire repository.
- If you change behavior, routes, data contracts, or major component structure, update this file in the same change.

## Do / Don't
- Do keep changes minimal, focused, and reversible.
- Do preserve existing project patterns (FastAPI routers + Vue pages/components/composables).
- Do validate changes with the most relevant local checks.
- Do prioritize the current agreed contract; backward compatibility is not required unless explicitly requested.
- Do keep private one-off scripts under `backend/data` undocumented in this file unless explicitly requested.
- Don't rewrite architecture unless explicitly asked.
- Don't add new dependencies unless required.
- Don't silently change API/data contracts.
- Don't add compatibility shims, legacy fallbacks, or dual-format support unless explicitly asked.

## Tech Stack
- Backend: FastAPI, pandas, openpyxl
- Frontend: Vue 3 + Vite
- Data source: `backend/data/purchases.xlsx`

## Current Data Contract
Workbook columns (required, case-sensitive):
- `ID, Item, Category, Cost, Date, Store, Tags, Notes`

Transactions API response fields (in this order):
- `ID, Item, Category, Cost, Date, Store, Tags, Notes`

Notes:
- Year filtering/listing is computed from `Date` in the backend.
- `Date` is returned as `YYYY-MM-DD`.

## Run Commands
From repo root:

Backend:
- `cd backend`
- `.venv/scripts/activate`
- `python server.py`
  - or `uvicorn server:app --reload --host 0.0.0.0 --port 8000`

Frontend:
- `cd frontend`
- `npm install`
- `npm run dev`
- `npm run build`

## Key Files
Backend:
- `backend/server.py` — FastAPI entry
- `backend/routers/transactions.py` — `/transactions` + `/transactions/years`
- `backend/routers/xlsx.py` — `/xlsx/reformat`
- `backend/excel/data_loader.py` — strict XLSX loading/normalization
- `backend/excel/handler.py` — remake/reformat logic
- `backend/scripts/rearrange_purchases_layout.py` — standalone layout migration script

Frontend:
- `frontend/src/composables/useGlobalFilters.js` — shared year/search/transactions state
- `frontend/src/components/FilterBar.vue` — year/search + Remake XLSX button
- `frontend/src/components/TransactionsTable.vue` — shared transactions table
- `frontend/src/config/storeIcons.js` — normalized store-name to icon mapping
- `frontend/src/composables/useChartData.js` — chart data transforms
- `frontend/src/pages/HomePage.vue`
- `frontend/src/pages/CategoryPage.vue`
- `frontend/src/pages/SettingsPage.vue` — unique store list + icon preview from transaction data

## UI/API Expectations
- Filter bar `Remake XLSX` button must call `POST /api/xlsx/reformat`.
- After remake succeeds, frontend should refresh transactions.
- Transactions tables should include: Date, Item, Category, Cost, Store, Tags, Notes.
- Search filtering should match `Item` and `Notes` fields only.
- Filter bar should include a tags multi-select; selecting multiple tags must apply OR matching against comma-separated `Tags` values.
- Filter bar should include a privacy mode toggle that masks always-visible dollar labels across cards/tables/charts while leaving tooltip values available on hover.
- Frontend route `/settings` should list unique stores from `/api/transactions/` and show mapped store icons when available.

## Safety Rules
- Create backups before destructive XLSX rewrites.
- Keep XLSX formatting rules consistent with `backend/excel/formats.py`.
- Preserve required headers/order unless explicitly asked to change them.
- Run one-off data mutation scripts with `--dry-run` first before applying writes.
- For notes-derived field upserts, clean consumed marker text from `Notes` when requested.

## Done Checklist
Before finishing a task:
- Verify changed endpoints still return expected JSON shape.
- Verify frontend components still consume that shape correctly.
- Run at least one relevant command (example: backend import check, frontend build/dev check).
- Update this file if behavior/contracts changed.
