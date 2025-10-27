# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator

st.set_page_config(layout="wide", page_title="TradingRevolution")

st.title("TradingRevolution – Zakładka Akcje")

# --- Wybór tickera ---
ticker = st.text_input("Wprowadź symbol giełdowy (np. AAPL)", value="AAPL").upper()

# --- Pobranie danych ---
try:
    df = yf.download(ticker, period="6mo", interval="1d")
    if df.empty:
        st.error("Nie znaleziono danych dla wybranego symbolu.")
        st.stop()
except Exception as e:
    st.error(f"Błąd pobierania danych: {e}")
    st.stop()

# --- Sprawdzenie wymaganych kolumn ---
required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
if not all(col in df.columns for col in required_cols):
    st.error(f"Brakuje wymaganych kolumn: {required_cols}")
    st.stop()

# --- Konwersja na numeryczne ---
for col in required_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Wskaźniki techniczne ---
df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
df['RSI14'] = RSIIndicator(df['Close'], 14).rsi()
macd = MACD(df['Close'])
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()

# --- Wyświetlenie metryk ---
col1, col2, col3 = st.columns(3)
col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}")
col2.metric("RSI (14)", f"{df['RSI14'].iloc[-1]:.2f}")
col3.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")

# --- Wykres świecowy ---
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name=ticker
)])
# Dodanie SMA
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='blue', width=1), name="SMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='orange', width=1), name="SMA50"))
fig.update_layout(title=f"Wykres świecowy {ticker}", xaxis_title="Data", yaxis_title="Cena")
st.plotly_chart(fig, use_container_width=True)

# --- Wskaźniki wolumenu ---
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Wolumen", marker_color='green'))
fig_vol.update_layout(title=f"Wolumen {ticker}", xaxis_title="Data", yaxis_title="Wolumen")
st.plotly_chart(fig_vol, use_container_width=True)

# --- Alert przykładowy ---
if df['RSI14'].iloc[-1] > 70:
    st.warning("RSI > 70 – możliwe wykupienie.")
elif df['RSI14'].iloc[-1] < 30:
    st.success("RSI < 30 – możliwe wyprzedanie.")
else:
    st.info("RSI w neutralnym zakresie.")

# --- Dane tabelaryczne ---
st.subheader(f"Dane {ticker}")
st.dataframe(df.tail(10))
