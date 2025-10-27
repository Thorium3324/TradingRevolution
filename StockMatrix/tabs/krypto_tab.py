# tabs/krypto_tab.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def krypto_tab():
    st.subheader("Zakładka Krypto - TradingRevolution Ultimate")

    ticker = st.text_input("Krypto ticker (np. BTC-USD, ETH-USD):", "BTC-USD").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"), key="start_date")
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today(), key="end_date")
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"], key="interval")

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

    # Dynamiczne kolumny
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col not in df.columns:
            st.error(f"Brakuje kolumny: {col}")
            return

    df = df.dropna(subset=['Close'])

    # --- Wskaźniki techniczne ---
    df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
    df['SMA200'] = SMAIndicator(df['Close'], 200).sma_indicator()
    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df['Close'], 50).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(df['High'], df['Low'], df['Close'], 14).stoch()
    df['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close'], 14).adx()

    # --- Wykres świecowy ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='lime',
        decreasing_line_color='red',
        name="Świece"
    ))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='blue', width=2), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='purple', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Panel wskaźników ---
    last_price = df['Close'].iloc[-1] if not df['Close'].empty else 0
    last_rsi = df['RSI'].iloc[-1] if not df['RSI'].empty else 0
    last_macd = df['MACD'].iloc[-1] if not df['MACD'].empty else 0
    volatility_30d = df['Close'].pct_change().dropna()[-30:].std() * 100 if len(df) >= 30 else 0

    cols = st.columns(4)
    cols[0].metric("Price (USD)", f"${last_price:.2f}")
    cols[1].metric("RSI (14)", f"{last_rsi:.2f}")
    cols[2].metric("MACD", f"{last_macd:.3f}")
    cols[3].metric("Volatility (30d)", f"{volatility_30d:.2f}%")
