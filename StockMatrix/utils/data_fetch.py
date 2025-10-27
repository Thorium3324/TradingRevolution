import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df = df.reset_index()
        df = df.set_index("Date")
        return df
    except Exception as e:
        print("Błąd pobierania danych:", e)
        return pd.DataFrame()
