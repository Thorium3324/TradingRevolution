import yfinance as yf
import pandas as pd

def get_stock_data(ticker, start, end, interval="1d"):
    df = yf.download(ticker, start=start, end=end, interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def find_price_columns(df):
    def find_col(keyword):
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col
        return None
    open_col = find_col("Open")
    high_col = find_col("High")
    low_col = find_col("Low")
    close_col = find_col("Close")
    volume_col = find_col("Volume")
    return open_col, high_col, low_col, close_col, volume_col
