import yfinance as yf
import pandas as pd

# Funkcja do pobierania danych akcji
def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df = df.reset_index().set_index("Date")
        return df
    except:
        return pd.DataFrame()

# Funkcja do pobierania danych kryptowalut
def get_crypto_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker+"-USD", period=period, interval=interval, progress=False)
        df = df.reset_index().set_index("Date")
        return df
    except:
        return pd.DataFrame()

# Funkcja pomocnicza do znalezienia kolumny z ceną zamknięcia
def find_price_columns(df):
    if "Close" in df.columns:
        return "Close"
    elif "Adj Close" in df.columns:
        return "Adj Close"
    return None
