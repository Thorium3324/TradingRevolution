import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period)
        df = df.dropna()
        df = df.rename(columns=str.strip)
        return df
    except Exception as e:
        print("Błąd pobierania danych:", e)
        return None

def get_crypto_data(symbol="BTC-USD", period="6mo"):
    try:
        df = yf.download(symbol, period=period)
        df = df.dropna()
        return df
    except Exception as e:
        print("Błąd pobierania danych krypto:", e)
        return None
