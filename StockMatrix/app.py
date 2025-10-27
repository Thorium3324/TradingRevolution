# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide")

st.title("TradingRevolution Ultimate 🚀")

# --- Zakładki ---
tabs = ["Akcje", "Krypto"]
selected_tab = st.sidebar.radio("Wybierz zakładkę:", tabs)

# --- Funkcja do pobrania i przygotowania danych ---
def get_data(ticker, start_date, end_date, interval):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        if df.empty:
            return None
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

# --- Funkcja do obliczenia wskaźników ---
def add_indicators(df):
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            st.warning(f"Brakuje kolumny: {col}")
            return df

    close = df['Close']
    high = df['High']
    low = df['Low']
    open_ = df['Open']
    volume = df['Volume']

    df['SMA20'] = SMAIndicator(close, 20).sma_indicator()
    df['SMA50'] = SMAIndicator(close, 50).sma_indicator()
    df['SMA200'] = SMAIndicator(close, 200).sma_indicator()
    df['EMA20'] = EMAIndicator(close, 20).ema_indicator()
    df['EMA50'] = EMAIndicator(close, 50).ema_indicator()
    df['RSI14'] = RSIIndicator(close, 14).rsi()
    macd = MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR14'] = AverageTrueRange(high, low, close, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(high, low, close, 14).stoch()
    df['CCI20'] = CCIIndicator(high, low, close, 20).cci()
    df['OBV'] = OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    df['ADX14'] = ADXIndicator(high, low, close, 14).adx()
    return df

# --- Funkcja do wyświetlenia panelu technicznego ---
def show_technical_panel(df):
    close = df['Close']
    last_price = close.iloc[-1]
    change_24h = ((close.iloc[-1] - close.iloc[-2])/close.iloc[-2]*100) if len(close) > 1 else 0
    rsi_val = df['RSI14'].iloc[-1]
    macd_val = df['MACD'].iloc[-1]
    vol_30d = close.pct_change().dropna()[-30:].std() * 100

    signal = "Neutral"
    signal_strength = 6
    if rsi_val < 30 and close.iloc[-1] > df['SMA20'].iloc[-1]:
        signal = "Buy"
        signal_strength = 8
    elif rsi_val > 70 and close.iloc[-1] < df['SMA20'].iloc[-1]:
        signal = "Sell"
        signal_strength = 7

    st.markdown("### Technical Analysis")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Price (USD)", f"${last_price:.2f}", f"{change_24h:.2f}%")
    col2.metric("RSI (14)", f"{rsi_val:.2f}")
    col3.metric("MACD", f"{macd_val:.3f}")
    col4.metric("Volatility (30d)", f"{vol_30d:.2f}%")
    col5.metric("Signal", f"{signal} ({signal_strength}/10)")

    if vol_30d > 10:
        st.warning("High volatility detected – expect larger price swings ⚠️")

# --- Funkcja do wyświetlenia wykresów ---
def show_charts(df, ticker):
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
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

# --- Zakładka Akcje ---
if selected_tab == "Akcje":
    st.subheader("Zakładka Akcje")

    ticker = st.text_input("Ticker akcji (np. AAPL, TSLA):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

    if ticker:
        df = get_data(ticker, start_date, end_date, interval)
        if df is not None:
            df = add_indicators(df)
            show_technical_panel(df)
            show_charts(df, ticker)
            st.subheader("Tabela wskaźników i sygnałów")
            st.dataframe(df.tail(20))

# --- Zakładka Krypto ---
elif selected_tab == "Krypto":
    st.subheader("Zakładka Krypto")

    ticker = st.text_input("Krypto ticker (np. BTC-USD, ETH-USD):", "BTC-USD").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"), key="krypto_start")
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today(), key="krypto_end")
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"], key="krypto_interval")

    if ticker:
        df = get_data(ticker, start_date, end_date, interval)
        if df is not None:
            df = add_indicators(df)
            show_technical_panel(df)
            show_charts(df, ticker)
            st.subheader("Tabela wskaźników i sygnałów")
            st.dataframe(df.tail(20))
