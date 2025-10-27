# tabs/krypto_tab.py - poprawiona wersja funkcji krypto_tab(), aby uniknąć KeyError przy braku kolumny 'Close'

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def krypto_tab():
    st.subheader("Zakładka Krypto - TradingRevolution Ultimate")

    # --- Dane wejściowe ---
    ticker = st.text_input("Krypto ticker (np. BTC-USD, ETH-USD):", "BTC-USD").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"), key="start_date")
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today(), key="end_date")
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"], key="interval")

    if not ticker:
        st.warning("Podaj ticker kryptowaluty")
        return

    # --- Pobranie danych ---
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

    # Spłaszczenie MultiIndex jeśli istnieje
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    # --- Dynamiczne dopasowanie kolumn ---
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

    required_cols = [open_col, high_col, low_col, close_col]
    if not all(required_cols):
        st.error("Brakuje wymaganych kolumn do wykresu świecowego")
        return

    df = df.dropna(subset=[col for col in required_cols if col is not None])

    open_data = df[open_col]
    high_data = df[high_col]
    low_data = df[low_col]
    close_data = df[close_col]

    # --- Wskaźniki ---
    df['SMA20'] = SMAIndicator(close_data, 20).sma_indicator()
    df['EMA20'] = EMAIndicator(close_data, 20).ema_indicator()
    df['RSI14'] = RSIIndicator(close_data, 14).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR14'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['Stochastic14'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()

    # --- Wykres świecowy ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(
        x=df.index,
        open=open_data,
        high=high_data,
        low=low_data,
        close=close_data,
        increasing_line_color='lime',
        decreasing_line_color='red',
        name="Świece"
    ))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Panel wskaźników ---
    st.subheader("Technical Analysis")
    last_price = close_data.iloc[-1]
    last_rsi = df['RSI14'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    last_volatility = close_data.pct_change().dropna()[-30:].std() * 100

    cols = st.columns(4)
    cols[0].metric("Price (USD)", f"${last_price:.2f}", key="price_metric")
    cols[1].metric("RSI (14)", f"{last_rsi:.2f}", key="rsi_metric")
    cols[2].metric("MACD", f"{last_macd:.2f}", key="macd_metric")
    cols[3].metric("Volatility 30d", f"{last_volatility:.2f}%", key="vol_metric")
