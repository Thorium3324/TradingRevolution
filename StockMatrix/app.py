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
        st.warning("Nie znaleziono danych dla wybranego symbolu.")
        st.stop()
except Exception as e:
    st.error(f"Błąd pobierania danych: {e}")
    st.stop()

# --- Obsługa kolumn w różnych formatach ---
df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]

# --- Sprawdzenie wymaganych kolumn ---
possible_cols = {
    'Open': [c for c in df.columns if 'Open' in c],
    'High': [c for c in df.columns if 'High' in c],
    'Low': [c for c in df.columns if 'Low' in c],
    'Close': [c for c in df.columns if 'Close' in c],
    'Volume': [c for c in df.columns if 'Volume' in c],
}

for key in possible_cols:
    if not possible_cols[key]:
        st.error(f"Brakuje kolumny: {key}")
        st.stop()
    # Bierzemy pierwszą pasującą kolumnę
    possible_cols[key] = possible_cols[key][0]

# --- Konwersja na numeryczne ---
for key, col in possible_cols.items():
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Wskaźniki techniczne ---
df['SMA20'] = SMAIndicator(df[possible_cols['Close']], 20).sma_indicator()
df['SMA50'] = SMAIndicator(df[possible_cols['Close']], 50).sma_indicator()
df['RSI14'] = RSIIndicator(df[possible_cols['Close']], 14).rsi()
macd = MACD(df[possible_cols['Close']])
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()

# --- Wyświetlenie metryk ---
col1, col2, col3 = st.columns(3)
col1.metric("Cena (USD)", f"${df[possible_cols['Close']].iloc[-1]:.2f}")
col2.metric("RSI (14)", f"{df['RSI14'].iloc[-1]:.2f}")
col3.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")

# --- Wykres świecowy ---
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df[possible_cols['Open']],
    high=df[possible_cols['High']],
    low=df[possible_cols['Low']],
    close=df[possible_cols['Close']],
    name=ticker
)])
# Dodanie SMA
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='blue', width=1), name="SMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='orange', width=1), name="SMA50"))
fig.update_layout(title=f"Wykres świecowy {ticker}", xaxis_title="Data", yaxis_title="Cena")
st.plotly_chart(fig, use_container_width=True)

# --- Wolumen ---
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(x=df.index, y=df[possible_cols['Volume']], name="Wolumen", marker_color='green'))
fig_vol.update_layout(title=f"Wolumen {ticker}", xaxis_title="Data", yaxis_title="Wolumen")
st.plotly_chart(fig_vol, use_container_width=True)

# --- Alert RSI ---
if df['RSI14'].iloc[-1] > 70:
    st.warning("RSI > 70 – możliwe wykupienie.")
elif df['RSI14'].iloc[-1] < 30:
    st.success("RSI < 30 – możliwe wyprzedanie.")
else:
    st.info("RSI w neutralnym zakresie.")

# --- Dane tabelaryczne ---
st.subheader(f"Dane {ticker}")
st.dataframe(df.tail(10))
