import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
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

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # --- Upewnienie się, że wszystkie kolumny to Series 1D ---
    def to_series(col):
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return pd.Series(col)

    open_data = to_series(df['Open']) if 'Open' in df.columns else None
    high_data = to_series(df['High']) if 'High' in df.columns else None
    low_data = to_series(df['Low']) if 'Low' in df.columns else None
    close_data = to_series(df['Close']) if 'Close' in df.columns else None
    volume_data = to_series(df['Volume']) if 'Volume' in df.columns else None

    if not all([open_data is not None, high_data is not None, low_data is not None, close_data is not None]):
        st.warning("Brakuje wymaganych kolumn do wykresu świecowego")
        return

    # --- Wskaźniki ---
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
    df['Stochastic14'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()

    # --- Wykres świecowy ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=open_data, high=high_data, low=low_data, close=close_data,
        increasing_line_color='lime', decreasing_line_color='red', name="Świece"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB_upper"))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB_lower"))
    fig.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark",
                      xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

 # --- Panel wskaźników ---
st.subheader("Technical Analysis")

last_price = float(close_data.iloc[-1]) if (not close_data.empty and pd.notna(close_data.iloc[-1])) else 0.0
last_rsi = float(df['RSI14'].iloc[-1]) if ('RSI14' in df.columns and pd.notna(df['RSI14'].iloc[-1])) else 0.0
last_macd = float(df['MACD'].iloc[-1]) if ('MACD' in df.columns and pd.notna(df['MACD'].iloc[-1])) else 0.0
last_volatility = float(close_data.pct_change().dropna()[-30:].std() * 100) if (len(close_data) >= 30 and close_data.pct_change().dropna()[-30:].std() is not None) else 0.0

cols = st.columns(4)
cols[0].metric("Price (USD)", f"${last_price:.2f}", key="price_metric")
cols[1].metric("RSI (14)", f"{last_rsi:.2f}", key="rsi_metric")
cols[2].metric("MACD", f"{last_macd:.2f}", key="macd_metric")
cols[3].metric("Volatility 30d", f"{last_volatility:.2f}%", key="vol_metric")

if last_volatility > 10:
    st.warning("High volatility detected – expect larger price swings ⚠️")
