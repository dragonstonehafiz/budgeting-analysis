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

    category_colors = {
        'Food & Beverages': '#E69F00',           # Orange
        'Books & Literature': '#56B4E9',         # Sky Blue
        'Gaming': '#009E73',                     # Bluish Green
        'Digital Subscriptions': '#F0E442',      # Yellow
        'Movies & Media': '#0072B2',             # Deep Blue
        'Music & Audio': '#D55E00',              # Vermilion
        'Electronics & Accessories': '#CC79A7',  # Reddish Purple
        'Clothing & Apparel': '#999999',         # Grey
        'Health & Personal Care': '#000000',     # Black
        'Collectibles': '#A6761D',               # Brownish Gold
        'Miscellaneous': '#DC267F'               # Bold Pink (well-separated from purple/blue)
    }
    
    return df, category_colors
    