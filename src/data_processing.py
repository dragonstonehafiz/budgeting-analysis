import pandas as pd
import os

def load_df(file_path):
    """
    Load a CSV file into a pandas DataFrame.
    
    Parameters:
    file_path (str): Path to the CSV file.
    
    Returns:
    pd.DataFrame: Loaded DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="cp1252")
    
    # Parse using dayfirst=True for DD/MM/YYYY style
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")
    df['Item'] = df['Item'].astype(str)
    df['Category'] = df['Category'].astype(str)
    # Extract Year and Month (as full month name or number)
    df['Year'] = df['Date'].dt.year
    df['Year'] = df['Date'].dt.year.astype(str)
    df['Month'] = df['Date'].dt.strftime('%b')  # 'Jan', 'Feb', etc.
    df['MonthNum'] = df['Date'].dt.month        # for sorting
    return df

def load_dfs():
    """
    Load all CSV files from the 'data' directory into a dictionary of DataFrames.
    
    Returns:
    dict: Dictionary where keys are filenames (without extension) and values are DataFrames.
    """
    if not os.path.exists("data"):
        os.makedirs("data")
        
    dfs = {}
    for filename in os.listdir("data"):
        if not filename.endswith(".csv"):
            continue
        if "combined" in filename:
            continue
        
        path = os.path.join("data", filename)
        df = load_df(path)
        key = filename.removesuffix(".csv")
        dfs[key] = df
        
        print(f"Loaded {filename} with {len(df)} rows. Null Entries: {df.isnull().sum().sum()}")
    
    return dfs

def create_combined_df(dfs: dict):
    combined = []
    for year, df in dfs.items():
        df = df.copy()
        combined.append(df)
        
    df_combined = pd.concat(combined, ignore_index=True)
    return df_combined
    

