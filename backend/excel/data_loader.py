"""Utility functions for loading data used by the PySide6 app.

This module provides a single `load_df` function that reads `data/purchases.xlsx`
and normalizes a few columns to stable types.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_df(filepath: str | Path = "data/purchases.xlsx") -> pd.DataFrame:
    """Load transactions from an Excel file into a pandas DataFrame.

    Ensures the expected columns exist and coerces common columns to strings.

    Expected columns (case-sensitive):
    - Item, Category, Cost, Date, Notes, Month, MonthNum, Year

    Returns:
        pd.DataFrame: loaded DataFrame with some columns coerced to str.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if required columns are missing.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"The file {filepath} does not exist.")

    df = pd.read_excel(filepath)

    # Normalize expected columns
    required = ["Item", "Category", "Cost", "Date", "Month", "MonthNum", "Year"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in Excel file: {missing}")

    # Coerce types: keep Cost numeric, Date as datetime, others as string
    df["Item"] = df["Item"].astype(str)
    df["Category"] = df["Category"].astype(str)
    # Cost may contain commas/strings; try coercion
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    # Parse dates if not already
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Year"].astype(str)

    if "Notes" in df.columns:
        df["Notes"] = df["Notes"].astype(str)

    return df
