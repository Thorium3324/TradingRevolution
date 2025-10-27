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
    ticker = st.text_input("Symbol akcji (np. AAPL, TSLA):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

    # Slider do okresów wskaźników
    sma_period = st.sidebar.slider("Okres SMA", 5, 200, 20)
    ema_period = st.sidebar.slider("Okres EMA", 5, 200, 20)
    rsi_period = st.sidebar.slider("Okres RSI", 5, 50, 14)
    stochastic_period = st.sidebar.slider("Okres Stochastic", 5, 50, 14)
    adx_period = st.sidebar.slider("Okres ADX", 5, 50, 14)
    atr_period = st.sidebar.slider("Okres ATR", 5, 50, 14)

    if not ticker:
        st.warning("Podaj symbol akcji")
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
        df.columns = [' '.join(map(str, col)).strip() for col in df.columns.values]

    # Konwersja kolumn na float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Dynamiczne dopasowanie kolumn ---
    def find_price_col(df, keyword):
        for col in df.columns:
            if keyword.lower() in str(col).lower():
                return col
        return None

    open_col = find_price_col(df, 'Open')
    high_col = find_price_col(df, 'High')
    low_col = find_price_col(df, 'Low')
    close_col = find_price_col(df, 'Close')
    volume_col = find_price_col(df, 'Volume')

    if not all([open_col, high_col, low_col, close_col]):
        st.error(f"Brakuje wymaganych kolumn do wykresu świecowego")
        return

    open_data = df[open_col]
    high_data = df[high_col]
    low_data = df[low_col]
    close_data = df[close_col]

    # --- Wskaźniki ---
    df['SMA'] = SMAIndicator(close_data, sma_period).sma_indicator()
    df['EMA'] = EMAIndicator(close_data, ema_period).ema_indicator()
    df['RSI'] = RSIIndicator(close_data, rsi_period).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(high_data, low_data, close_data, atr_period).average_true_range()
    df['Stochastic'] = StochasticOscillator(high_data, low_data, close_data, stochastic_period).stoch()
    df['ADX'] = ADXIndicator(high_data, low_data, close_data, adx_period).adx()

    # --- Sygnały Buy/Sell ---
    df['Signal'] = ""
    df.loc[(close_data > df['SMA']) & (df['RSI'] < 70), 'Signal'] = "BUY"
    df.loc[(close_data < df['SMA']) & (df['RSI'] > 30), 'Signal'] = "SELL"

    # --- Formacje świecowe ---
    df['Hammer'] = ((high_data - low_data) > 3*(open_data - close_data)) & \
                   (((close_data - low_data) / (0.001 + high_data - low_data)) > 0.6)
    df['Doji'] = abs(close_data - open_data) / (high_data - low_data + 0.001) < 0.1
    df['Engulfing'] = ((close_data > open_data) & (close_data.shift(1) < open_data.shift(1)) & \
                       (close_data > open_data.shift(1))) | \
                      ((close_data < open_data) & (close_data.shift(1) > open_data.shift(1)) & \
                       (close_data < open_data.shift(1)))

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
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=2), name=f"SMA {sma_period}"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA'], line=dict(color='green', width=2), name=f"EMA {ema_period}"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    # --- RSI ---
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title=f"RSI ({rsi_period})", template="plotly_dark", height=250)

    # --- MACD ---
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='cyan', width=2), name="MACD"))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], line=dict(color='yellow', width=2), name="MACD Signal"))
    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)

    # --- Wolumen ---
    if volume_col:
        volume_data = df[volume_col]
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df.index, y=volume_data, name="Wolumen", marker_color='blue'))
        fig_vol.update_layout(title="Wolumen", template="plotly_dark", height=200)
        st.plotly_chart(fig_vol, use_container_width=True)

    # --- Wyświetlenie wykresów ---
    st.plotly_chart(fig_candle, use_container_width=True)
    st.plotly_chart(fig_rsi, use_container_width=True)
    st.plotly_chart(fig_macd, use_container_width=True)

    # --- Technical Analysis Panel ---
    price = close_data[-1]
    change_24h = ((close_data[-1] - close_data[-2])/close_data[-2]*100) if len(close_data) > 1 else 0
    rsi_value = df['RSI'][-1]
    macd_value = df['MACD'][-1]
    volatility_30d = close_data.pct_change().dropna()[-30:].std() * 100

    signal_strength = 6
    signal = "Neutral"
    if rsi_value < 30 and close_data[-1] > df['SMA'][-1]:
        signal = "Buy"
        signal_strength = 8
    elif rsi_value > 70 and close_data[-1] < df['SMA'][-1]:
        signal = "Sell"
        signal_strength = 7

    st.markdown("### Technical Analysis")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Price (USD)", f"${price:.2f}", f"{change
