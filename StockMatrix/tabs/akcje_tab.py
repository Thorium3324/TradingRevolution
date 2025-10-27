import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def akcje_tab():
    st.subheader("Zakładka Akcje - TradingRevolution Ultimate")

    ticker = st.text_input("Ticker akcji (np. AAPL, MSFT):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1wk", "1mo"])

    if not ticker:
        st.warning("Podaj ticker akcji")
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

    # Dynamiczne dopasowanie kolumn
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
        st.error(f"Brakuje wymaganych kolumn do wykresu świecowego")
        return

    # Konwersja kolumn na float
    for col in required_cols + ([volume_col] if volume_col else []):
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Wskaźniki techniczne ---
    close_data = df[close_col]
    high_data = df[high_col]
    low_data = df[low_col]
    open_data = df[open_col]

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
    if volume_col:
        df['OBV'] = OnBalanceVolumeIndicator(close_data, df[volume_col]).on_balance_volume()

    # --- Sygnały ---
    df['Signal'] = ""
    df.loc[(close_data > df['SMA50']) & (df['RSI14'] < 70), 'Signal'] = "BUY"
    df.loc[(close_data < df['SMA50']) & (df['RSI14'] > 30), 'Signal'] = "SELL"

    # --- Formacje świecowe ---
    df['Hammer'] = ((high_data - low_data) > 3*(open_data - close_data)) & \
                   (((close_data - low_data) / (0.001 + high_data - low_data)) > 0.6)
    df['Doji'] = abs(close_data - open_data) / (high_data - low_data + 0.001) < 0.1
    df['Engulfing'] = ((close_data > open_data) & (close_data.shift(1) < open_data.shift(1)) & \
                       (close_data > open_data.shift(1))) | \
                      ((close_data < open_data) & (close_data.shift(1) > open_data.shift(1)) & \
                       (close_data < open_data.shift(1)))

    # --- Wykresy ---
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
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=2), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='red', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='purple', width=2), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI14'], line=dict(color='magenta', width=2), name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title="RSI (14)", template="plotly_dark", height=250)

    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='cyan', width=2), name="MACD"))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], line=dict(color='yellow', width=2), name="MACD Signal"))
    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)

    if volume_col:
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df.index, y=df[volume_col], name="Wolumen", marker_color='blue'))
        fig_vol.update_layout(title="Wolumen", template="plotly_dark", height=200)
        st.plotly_chart(fig_vol, use_container_width=True)

    st.plotly_chart(fig_candle, use_container_width=True)
    st.plotly_chart(fig_rsi, use_container_width=True)
    st.plotly_chart(fig_macd, use_container_width=True)

    # --- Technical Analysis Panel ---
    price = close_data[-1]
    change_24h = ((close_data[-1] - close_data[-2])/close_data[-2]*100) if len(close_data) > 1 else 0
    rsi_value = df['RSI14'][-1]
    macd_value = df['MACD'][-1]
    volatility_30d = close_data.pct_change().dropna()[-30:].std() * 100

    signal_strength = 6
    signal = "Neutral"
   
