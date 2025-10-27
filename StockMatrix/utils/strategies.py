import yfinance as yf
import streamlit as st
import pandas as pd

def moving_average_strategy(symbol, short_window, long_window):
    df = yf.download(symbol, period="1y")
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    df["Signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()

    st.write("📈 Strategia: Krzyżowanie średnich kroczących")
    st.line_chart(df[["Close", "SMA_short", "SMA_long"]])
    st.write(df.tail())
