import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator

def akcje_tab():
    st.title("Zakładka Akcje")

    ticker = st.text_input("Wpisz ticker:", "AAPL").upper()

    # Pobranie danych z obsługą błędów
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
    except Exception:
        df = pd.DataFrame()

    # Jeśli brak danych, użyj placeholder
    if df.empty:
        df = pd.DataFrame({
            'Open': [0],
            'High': [0],
            'Low': [0],
            'Close': [0],
            'Volume': [0]
        }, index=pd.to_datetime([pd.Timestamp.today()]))

    # Upewnij się, że kolumny istnieją i są Series 1D
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col not in df.columns:
            possible_cols = [c for c in df.columns if col in c]
            if possible_cols:
                df[col] = pd.Series(df[possible_cols[0]].values)
            else:
                df[col] = pd.Series([0]*len(df))
        else:
            # Konwertuj na Series 1D
            if isinstance(df[col], pd.DataFrame):
                df[col] = pd.Series(df[col].values.flatten())
            else:
                df[col] = pd.Series(df[col].values)

    # Wskaźniki techniczne
    try:
        df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
    except Exception:
        df['SMA20'] = df['Close']  # fallback, gdy mało danych

    # Wykres świecowy
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    )])
    st.plotly_chart(fig, use_container_width=True)

    # Metryki
    col1, col2 = st.columns(2)
    col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}")
    col2.metric("SMA20", f"${df['SMA20'].iloc[-1]:.2f}")
