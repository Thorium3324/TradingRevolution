import yfinance as yf
import ccxt
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df

@st.cache_data(ttl=600)
def get_crypto_data(exchange_name, symbol, timeframe='1h', limit=500):
    exchange_class = getattr(ccxt, exchange_name)()
    bars = exchange_class.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp','Open','High','Low','Close','Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df
