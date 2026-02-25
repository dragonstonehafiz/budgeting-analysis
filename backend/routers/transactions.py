"""
Transactions router — serves raw transaction data from purchases.xlsx.
"""
from fastapi import APIRouter, Query
from excel.data_loader import load_df

router = APIRouter()


@router.get("/")
def get_transactions(year: str = Query(default=None, description="Filter by year, e.g. '2025'")):
    """Return all transactions, optionally filtered by year."""
    df = load_df("data/purchases.xlsx")
    result = df.copy()
    if year:
        result = result[result["Date"].dt.year.astype(str) == year]
    result["Date"] = result["Date"].dt.strftime("%Y-%m-%d")
    response_cols = ["ID", "Item", "Category", "Cost", "Date", "Store", "Tags", "Notes"]
    return result[response_cols].to_dict(orient="records")


@router.get("/years")
def get_years():
    """Return the list of distinct years present in the data."""
    df = load_df("data/purchases.xlsx")
    years = sorted(df["Date"].dt.year.dropna().astype(int).astype(str).unique().tolist())
    return {"years": years}
