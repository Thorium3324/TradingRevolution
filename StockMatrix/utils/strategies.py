import yfinance as yf
import streamlit as st

def moving_average_strategy(symbol, short_window=10, long_window=50):
    df = yf.download(symbol, period="1y")
    if df is None or df.empty:
        st.error("Brak danych dla strategii")
        return
    df["SMA_short"] = df["Close"].rolling(short_window).mean()
    df["SMA_long"] = df["Close"].rolling(long_window).mean()
    df["Signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    st.line_chart(df[["Close","SMA_short","SMA_long"]].dropna())
    st.write(df.tail())
