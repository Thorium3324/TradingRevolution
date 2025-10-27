import yfinance as yf
import pandas as pd

def _flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(map(str, c)).strip() for c in df.columns.values]
    df.columns = [str(c).strip() for c in df.columns]
    return df

def get_stock_data(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = _flatten_columns(df)
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(how='all')
        return df
    except Exception as e:
        print("data_fetch.get_stock_data error:", e)
        return pd.DataFrame()

def get_crypto_data(symbol="BTC-USD", period="6mo", interval="1d"):
    return get_stock_data(symbol, period=period, interval=interval)

def find_price_columns(df):
    # find most likely Open/High/Low/Close/Volume columns (case/variant-insensitive)
    def find_col(keyword):
        for c in df.columns:
            if keyword.lower() in c.lower():
                return c
        return None
    open_c = find_col("open")
    high_c = find_col("high")
    low_c = find_col("low")
    close_c = find_col("close")
    vol_c = find_col("volume")
    return open_c, high_c, low_c, close_c, vol_c
