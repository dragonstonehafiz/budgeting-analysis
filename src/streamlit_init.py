import pandas as pd
import os
from src.data_processing import load_df, load_dfs, create_combined_df

def load_combined() -> pd.DataFrame:
    combined_df_path = "data/combined.csv"
    if os.path.exists(combined_df_path):
        return load_df(combined_df_path)
    else:
        dfs = load_dfs()
        combined_df = create_combined_df(dfs)
        combined_df.to_csv(combined_df_path, index=False)
        return load_df(combined_df_path)

def init():
    # Load data
    df = load_combined()

    # Set colors for bars
    category_colors = {
        'Food & Beverages': '#B22222',           # Meat Red
        'Books & Literature': '#6A0DAD',         # Regal Purple
        'Gaming': '#AAFF00',                     # Xbox Green
        'Digital Subscriptions': '#FFD700',      # Bright Yellow
        'Movies & Media': '#1E90FF',             # Dodger Blue
        'Music & Audio': '#FF69B4',              # Bright Pink
        'Electronics & Accessories': '#00FFFF',  # Aqua Blue
        'Clothing & Apparel': '#C71585',         # Dark Pink
        'Health & Personal Care': '#006400',     # Dark Green
        'Collectibles': '#FF4500',               # Fire Orange
        'Miscellaneous': '#808080'               # Grey
    }
    
    return df, category_colors
    