# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator

@st.cache_data(ttl=3600)
def get_stock_data(symbol="AAPL"):
    try:
        df = yf.download(symbol, period="1y", interval="1d")
        if df.empty:
            return None

        # Flatten MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]

        # If Close missing but Adj Close exists
        if 'Close' not in df.columns and 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']

        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        existing_cols = [col for col in required_cols if col in df.columns]

        if not existing_cols:
            return None  # Brak danych

        return df

    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

def add_technical_indicators(df):
    df = df.copy()
    if 'Close' not in df.columns or df['Close'].empty:
        return df

    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    df['SMA20'] = SMAIndicator(close, 20).sma_indicator()
    df['SMA50'] = SMAIndicator(close, 50).sma_indicator()
    df['EMA20'] = EMAIndicator(close, 20).ema_indicator()
    df['RSI'] = RSIIndicator(close, 14).rsi()
    return df

def akcje_tab():
    st.header("📈 Zakładka Akcje")

    ticker = st.text_input("Wpisz symbol akcji (np. AAPL):", "AAPL").upper()
    if not ticker:
        st.info("Wpisz symbol akcji, aby wyświetlić dane.")
        return

    df = get_stock_data(ticker)
    if df is None:
        st.warning("Nie znaleziono danych dla wybranego symbolu.")
        return

    df = add_technical_indicators(df)

    # Wyświetlanie metryk jeśli kolumna Close istnieje
    if 'Close' in df.columns and not df['Close'].empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}" if not df['Close'].empty else "N/A")
        col2.metric("SMA20", f"${df['SMA20'].iloc[-1]:.2f}" if 'SMA20' in df.columns else "N/A")
        col3.metric("SMA50", f"${df['SMA50'].iloc[-1]:.2f}" if 'SMA50' in df.columns else "N/A")
        col4.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}" if 'RSI' in df.columns else "N/A")

    # Wykres świecowy z wolumenem
    st.subheader(f"Wykres świecowy dla {ticker}")
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if all(col in df.columns for col in required_cols):
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=ticker
        ))
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Wolumen",
            marker_color='blue',
            yaxis='y2'
        ))
        fig.update_layout(
            yaxis=dict(title='Cena'),
            yaxis2=dict(title='Wolumen', overlaying='y', side='right', showgrid=False, position=0.15),
            xaxis_rangeslider_visible=False,
            height=600,
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Brak pełnych danych do wykresu świecowego.")

    # Ostatnie 10 wierszy
    st.subheader("Ostatnie dane")
    st.dataframe(df.tail(10))
