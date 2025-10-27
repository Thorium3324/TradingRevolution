import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def akcje_tab():
    st.subheader("Zakładka Akcje - TradingRevolution Ultimate")

    # --- Dane wejściowe ---
    ticker = st.text_input("Wprowadź ticker akcji (np. AAPL, TSLA):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"), key=f"start_{ticker}")
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today(), key=f"end_{ticker}")
    interval = st.selectbox("Interwał:", ["1d", "1wk", "1mo"], key=f"interval_{ticker}")

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

    # Konwersja kolumn na float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Wyszukiwanie wymaganych kolumn ---
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
    df['CCI20'] = CCIIndicator(high_data, low_data, close_data, 20).cci()
    df['Stochastic14'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()
    df['ATR14'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['ADX14'] = ADXIndicator(high_data, low_data, close_data, 14).adx()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    # --- Wykres świecowy z wskaźnikami ---
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
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=1), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='purple', width=1), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=1), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue', width=1), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

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

if not all([open_col, high_col, low_col, close_col]):
    st.error("Brakuje wymaganych kolumn do wykresu świecowego")
    return

open_data = df[open_col]
high_data = df[high_col]
low_data = df[low_col]
close_data = df[close_col]

# Wolumen (przypisanie do zmiennej)
volume_data = df[volume_col] if volume_col else None

# --- Wolumen jako słupki ---
if volume_data is not None:
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(
        x=df.index,
        y=volume_data,
        marker_color='rgba(135, 206, 235, 0.7)',  # lekko przezroczysty niebieski
        name='Wolumen'
    ))
    fig_vol.update_layout(
        title="Wolumen",
        template="plotly_dark",
        height=350,
        margin=dict(t=40, b=20),
        xaxis=dict(rangeslider=dict(visible=False)),
    )
    st.plotly_chart(fig_vol, use_container_width=True)
