# Poprawiona wersja tabs/krypto_tab.py, która działa bez błędu ImportError
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def krypto_tab():
    st.subheader("Zakładka Krypto")

    ticker = st.text_input("Krypto ticker (np. BTC-USD):", "BTC-USD").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

    if not ticker:
        st.warning("Podaj ticker kryptowaluty")
        return

    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return

    if df.empty:
        st.warning(f"Brak danych dla {ticker}")
        return

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Znalezienie kolumn ---
    def find_price_col(df, keyword):
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col
        return None

    open_col = find_price_col(df, 'Open')
    high_col = find_price_col(df, 'High')
    low_col = find_price_col(df, 'Low')
    close_col = find_price_col(df, 'Close')
    volume_col = find_price_col(df, 'Volume')

    if not all([open_col, high_col, low_col, close_col]):
        st.error("Brakuje wymaganych kolumn do wykresu świecowego")
        return

    open_data = df[open_col]
    high_data = df[high_col]
    low_data = df[low_col]
    close_data = df[close_col]
    volume_data = df[volume_col] if volume_col else None

    # --- Wskaźniki techniczne ---
    df['SMA20'] = SMAIndicator(close_data, 20).sma_indicator()
    df['SMA50'] = SMAIndicator(close_data, 50).sma_indicator()
    df['SMA200'] = SMAIndicator(close_data, 200).sma_indicator()
    df['EMA20'] = EMAIndicator(close_data, 20).ema_indicator()
    df['EMA50'] = EMAIndicator(close_data, 50).ema_indicator()
    df['RSI14'] = RSIIndicator(close_data, 14).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR14'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()
    df['CCI20'] = CCIIndicator(high_data, low_data, close_data, 20).cci()
    df['ADX14'] = ADXIndicator(high_data, low_data, close_data, 14).adx()
    if volume_data is not None:
        df['OBV'] = OnBalanceVolumeIndicator(close_data, volume_data).on_balance_volume()

    # --- Wykres świecowy ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=open_data,
                                 high=high_data,
                                 low=low_data,
                                 close=close_data,
                                 increasing_line_color='lime',
                                 decreasing_line_color='red'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=2), name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='blue', width=2), name="SMA200"))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='purple', width=2), name="EMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig.update_layout(title=f"{ticker} - Wskaźniki techniczne", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- Panel wskaźników ---
    st.subheader("Technical Analysis")
    cols = st.columns(6)
    cols[0].metric("Price (USD)", f"${close_data[-1]:.2f}")
    cols[1].metric("RSI14", f"{df['RSI14'][-1]:.2f}")
    cols[2].metric("MACD", f"{df['MACD'][-1]:.2f}")
    cols[3].metric("ATR14", f"{df['ATR14'][-1]:.2f}")
    cols[4].metric("ADX14", f"{df['ADX14'][-1]:.2f}")
    if volume_data is not None:
        cols[5].metric("OBV", f"{df['OBV'][-1]:.2f}")
