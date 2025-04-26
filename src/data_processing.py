import pandas as pd
import os

def load_df(filepath = "data/purchases.xlsx") -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    
    df = pd.read_excel(filepath)  
    df['Item'] = df['Item'].astype(str)
    df['Category'] = df['Category'].astype(str)
    df['Year'] = df['Year'].astype(str)

    return df    

