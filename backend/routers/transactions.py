"""
Transactions router — serves raw transaction data from purchases.xlsx.
"""
from fastapi import APIRouter, Query
from excel.data_loader import load_df

router = APIRouter()

# Load once at startup — crashes intentionally if the file is missing
df = load_df("data/purchases.xlsx")


@router.get("/")
def get_transactions(year: str = Query(default=None, description="Filter by year, e.g. '2025'")):
    """Return all transactions, optionally filtered by year."""
    result = df.copy()
    if year:
        result = result[result["Year"].astype(str) == year]
    result["Date"] = result["Date"].dt.strftime("%Y-%m-%d")
    return result.to_dict(orient="records")


@router.get("/years")
def get_years():
    """Return the list of distinct years present in the data."""
    years = sorted(df["Year"].astype(str).unique().tolist())
    return {"years": years}
