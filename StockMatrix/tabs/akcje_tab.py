# tabs/akcje_tab.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator

def akcje_tab():
    st.title("📈 Analiza Akcji")

    ticker = st.text_input("Podaj ticker akcji:", "AAPL").upper()
    if not ticker:
        st.warning("Podaj ticker akcji, aby rozpocząć analizę.")
        return

    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    except Exception as e:
        st.error(f"❌ Błąd pobierania danych: {e}")
        return

    if df.empty:
        st.error(f"❌ Nie udało się pobrać danych dla {ticker}")
        return

    df = df.reset_index()

    # Mapowanie kolumn do standardowych nazw
    col_map = {}
    for col in df.columns:
        lname = col.lower()
        if 'open' in lname:
            col_map['Open'] = col
        elif 'high' in lname:
            col_map['High'] = col
        elif 'low' in lname:
            col_map['Low'] = col
        elif 'close' in lname:
            col_map['Close'] = col
        elif 'volume' in lname:
            col_map['Volume'] = col

    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    existing_cols = [k for k in required if k in col_map]

    if not existing_cols:
        st.error("❌ Brak wymaganych kolumn w danych.")
        return

    # Konwersja kolumn do numeric
    for col in existing_cols:
        df[col] = pd.to_numeric(pd.Series(df[col_map[col]].values.flatten()), errors='coerce')

    # Dropna tylko po istniejących kolumnach
    df = df.dropna(subset=existing_cols)
    if df.empty:
        st.error("❌ Dane po konwersji są puste.")
        return

    close_col = 'Close'

    # Metryki
    col1, col2, col3 = st.columns(3)
    col1.metric("Cena (USD)", f"${df[close_col].iloc[-1]:.2f}")
    col2.metric("Zmiana 24h", f"{(df[close_col].pct_change().iloc[-1]*100):.2f}%" if len(df) > 1 else "Brak danych")

    # Wskaźniki techniczne
    if 'Close' in df.columns:
        df['SMA20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['EMA20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
        df['RSI14'] = RSIIndicator(df['Close'], window=14).rsi()
        col3.metric("RSI (14)", f"{df['RSI14'].iloc[-1]:.2f}" if not df['RSI14'].isna().all() else "Brak danych")

    # Wykres świecowy
    st.markdown("### Wykres świecowy z SMA/EMA")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    ))
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA20'], mode='lines', name='SMA20', line=dict(color='orange')))
    if 'EMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], mode='lines', name='EMA20', line=dict(color='g_
