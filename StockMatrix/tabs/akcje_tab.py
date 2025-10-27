import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def akcje_tab():
    st.subheader("Zakładka Akcje - TradingRevolution Ultimate")

    # --- Dane wejściowe ---
    ticker = st.text_input("Wprowadź ticker akcji:", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1wk"])

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
        st.warning("Brak danych dla wybranego symbolu")
        return

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # --- Konwersja kolumn na float ---
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Sprawdzenie wymaganych kolumn ---
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Brakuje kolumny: {col}")
            return

    close_data = df['Close']
    high_data = df['High']
    low_data = df['Low']
    open_data = df['Open']
    volume_data = df['Volume']

    # --- Wskaźniki techniczne ---
    df['SMA20'] = SMAIndicator(close_data, 20).sma_indicator()
    df['SMA50'] = SMAIndicator(close_data, 50).sma_indicator()
    df['SMA200'] = SMAIndicator(close_data, 200).sma_indicator()
    df['EMA20'] = EMAIndicator(close_data, 20).ema_indicator()
    df['EMA50'] = EMAIndicator(close_data, 50).ema_indicator()
    df['RSI'] = RSIIndicator(close_data, 14).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['BB_upper'] = BollingerBands(close_data, 20, 2).bollinger_hband()
    df['BB_lower'] = BollingerBands(close_data, 20, 2).bollinger_lband()
    df['ATR'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()
    df['ADX'] = ADXIndicator(high_data, low_data, close_data, 14).adx()

    # --- Wykres świecowy ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(
        x=df.index, open=open_data, high=high_data, low=low_data, close=close_data,
        increasing_line_color='lime', decreasing_line_color='red', name="Świece"
    ))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=2), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='blue', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='pink', width=2), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Panel technicznej analizy ---
    price = close_data.iloc[-1]
    change_24h = ((close_data.iloc[-1] - close_data.iloc[-2])/close_data.iloc[-2]*100) if len(close_data) > 1 else 0
    rsi_value = df['RSI'].iloc[-1]
    macd_value = df['MACD'].iloc[-1]
    volatility_30d = close_data.pct_change().dropna()[-30:].std() * 100

    signal_strength = 6
    signal = "Neutral"
    if rsi_value < 30 and close_data.iloc[-1] > df['SMA20'].iloc[-1]:
        signal = "Buy"
        signal_strength = 8
    elif rsi_value > 70 and close_data.iloc[-1] < df['SMA20'].iloc[-1]:
        signal = "Sell"
        signal_strength = 7

    st.markdown("### Technical Analysis")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Price (USD)", f"${price:.2f}", f"{change_24h:.2f}%")
    col2.metric("RSI (14)", f"{rsi_value:.2f}")
    col3.metric("MACD", f"{macd_value:.3f}")
    col4.metric("Volatility (30d)", f"{volatility_30d:.2f}%")
    col5.metric("Signal", f"{signal} ({signal_strength}/10)")

    if volatility_30d > 10:
        st.warning("High volatility detected – expect larger price swings ⚠️")
