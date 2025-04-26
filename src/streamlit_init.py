import pandas as pd
import os
from src.data_processing import load_df

def load_combined() -> pd.DataFrame:
    df_path = "data/purchases.xlsx"
    if os.path.exists(df_path):
        return load_df(df_path)
    else:
        raise FileNotFoundError(f"{df_path} does not exist.")

def init():
    # Load data
    df = load_combined()
    
    category_colors = {
        'Food & Beverages': '#D9D9D9',
        'Books & Literature': '#e9a9ff',
        'Gaming': '#bbe33d',
        'Digital Subscriptions': '#fbffa9',
        'Movies & Media': '#a05eff',
        'Music & Audio': '#ffa9f2',
        'Electronics & Accessories': '#729fcf',
        'Clothing & Apparel': '#D9D9D9',
        'Health & Personal Care': '#a9ffc4',
        'Collectibles': '#ffc85d',
        'Miscellaneous': '#D9D9D9'
    }
    
    return df, category_colors
    