import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

st.set_page_config(page_title="TradingRevolution - Akcje", layout="wide")

st.title("TradingRevolution - Zakładka Akcje")

# --- Dane wejściowe ---
ticker = st.text_input("Ticker akcji (np. AAPL, TSLA, MSFT):", "AAPL").upper()
start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

# --- Pobranie danych ---
if ticker:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        st.stop()

    if df.empty:
        st.warning(f"Brak danych dla {ticker}")
        st.stop()

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Konwersja kolumn na float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

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
        st.error(f"Brakuje wymaganych kolumn do wykresu świecowego: {required_cols}")
        st.stop()

    # --- Wskaźniki techniczne ---
    df['SMA20'] = SMAIndicator(df[close_col], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df[close_col], 50).sma_indicator()
    df['SMA200'] = SMAIndicator(df[close_col], 200).sma_indicator()
    df['EMA20'] = EMAIndicator(df[close_col], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df[close_col], 50).ema_indicator()
    df['RSI'] = RSIIndicator(df[close_col], 14).rsi()
    macd = MACD(df[close_col])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(df[close_col])
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(df[high_col], df[low_col], df[close_col], 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(df[high_col], df[low_col], df[close_col], 14).stoch()
    df['ADX'] = ADXIndicator(df[high_col], df[low_col], df[close_col], 14).adx()
    df['CCI'] = CCIIndicator(df[high_col], df[low_col], df[close_col], 20).cci()
    df['OBV'] = OnBalanceVolumeIndicator(df[close_col], df[volume_col]).on_balance_volume()

    # --- Sygnały BUY/SELL ---
    df['Signal'] = ""
    df.loc[(df[close_col] > df['SMA20']) & (df['RSI'] < 70), 'Signal'] = "BUY"
    df.loc[(df[close_col] < df['SMA20']) & (df['RSI'] > 30), 'Signal'] = "SELL"

    # --- Wykres świecowy ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(
        x=df.index,
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        increasing_line_color='lime',
        decreasing_line_color='red',
        name="Świece"
    ))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=2), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='purple', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue', width=2), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Panel Technical Analysis ---
    st.markdown("### Technical Analysis")
    col1, col2, col3, col4, col5 = st.columns(5)
    last_close = df[close_col].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    vol_30d = df[close_col].pct_change().dropna()[-30:].std() * 100

    signal_strength = 6
    signal = "Neutral"
    if last_rsi < 30 and last_close > df['SMA20'].iloc[-1]:
        signal = "Buy"
        signal_strength = 8
    elif last_rsi > 70 and last_close < df['SMA20'].iloc[-1]:
        signal = "Sell"
        signal_strength = 7

    col1.metric("Price (USD)", f"${last_close:.2f}")
    col2.metric("RSI (14)", f"{last_rsi:.2f}")
    col3.metric("MACD", f"{last_macd:.2f}")
    col4.metric("Volatility (30d)", f"{vol_30d:.2f}%")
    col5.metric("Signal", f"{signal} ({signal_strength}/10)")

    # --- Tabela wskaźników ---
    st.subheader("Ostatnie wskaźniki i sygnały")
    st.dataframe(df[['SMA20','SMA50','SMA200','EMA20','EMA50','RSI','MACD','MACD_signal',
                     'BB_upper','BB_lower','ATR','Stochastic','ADX','CCI','OBV','Signal']].tail(20))
