"""Utility functions for loading data used by the PySide6 app.

This module provides a single `load_df` function that reads `data/purchases.xlsx`
and normalizes a few columns to stable types.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_df(filepath: str | Path = "data/purchases.xlsx") -> pd.DataFrame:
    """Load transactions from an Excel file into a pandas DataFrame.

    Ensures required columns exist and coerces common columns to stable types.
    Expected workbook schema:
    ID, Item, Category, Cost, Date, Store, Tags, Notes.

    Required columns (case-sensitive):
    - ID, Item, Category, Cost, Date, Store, Tags, Notes

    Returns:
        pd.DataFrame: loaded DataFrame with some columns coerced to str.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if required columns are missing.
    """
    filepath = Path(filepath)
    if not filepath.is_absolute():
        backend_root = Path(__file__).resolve().parents[1]
        filepath = backend_root / filepath
    if not filepath.exists():
        raise FileNotFoundError(f"The file {filepath} does not exist.")

    df = pd.read_excel(filepath)

    # Normalize required columns
    required = ["ID", "Item", "Category", "Cost", "Date", "Store", "Tags", "Notes"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in Excel file: {missing}")

    # Coerce types: keep Cost numeric, Date as datetime, others as string
    # Handle text "nan" values by filling nulls first.
    df["Item"] = df["Item"].astype(str)
    df["Category"] = df["Category"].astype(str)
    # Cost may contain commas/strings; try coercion
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    # Parse dates if not already
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["ID"] = pd.to_numeric(df["ID"], errors="coerce").fillna(0).astype(int)
    df["Store"] = df["Store"].fillna("").astype(str)
    df["Tags"] = df["Tags"].fillna("").astype(str)
    df["Notes"] = df["Notes"].fillna("").astype(str)

    # Keep only rows with the minimum required fields present.
    df = df[df["Item"].str.strip() != ""]
    df = df[df["Date"].notna()]
    df = df[df["Cost"].notna()]

    return df
