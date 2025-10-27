import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, MomentumIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def krypto_tab():
    st.subheader("Zakładka Krypto - TradingRevolution Ultimate")

    # --- Dane wejściowe ---
    ticker = st.text_input("Krypto ticker (np. BTC-USD, ETH-USD):", "BTC-USD").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

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

    df.index = pd.to_datetime(df.index)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Dynamiczne dopasowanie kolumn ---
    def find_col(df, keyword):
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col
        return None

    open_col = find_col(df, 'Open')
    high_col = find_col(df, 'High')
    low_col = find_col(df, 'Low')
    close_col = find_col(df, 'Close')
    volume_col = find_col(df, 'Volume')

    if not all([open_col, high_col, low_col, close_col]):
        st.error(f"Brakuje wymaganych kolumn do wykresu świecowego")
        return

    open_data = df[open_col]
    high_data = df[high_col]
    low_data = df[low_col]
    close_data = df[close_col]
    volume_data = df[volume_col] if volume_col else pd.Series([0]*len(df), index=df.index)

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
    bb = BollingerBands(close_data, window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR14'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()
    df['CCI20'] = CCIIndicator(high_data, low_data, close_data, 20).cci()
    df['Momentum5'] = MomentumIndicator(close_data, 5).momentum()
    df['OBV'] = OnBalanceVolumeIndicator(close_data, volume_data).on_balance_volume()
    df['ADX14'] = ADXIndicator(high_data, low_data, close_data, 14).adx()

    # --- Sygnały Buy/Sell ---
    df['Signal'] = ""
    df.loc[(close_data > df['SMA20']) & (df['RSI14'] < 70), 'Signal'] = "BUY"
    df.loc[(close_data < df['SMA20']) & (df['RSI14'] > 30), 'Signal'] = "SELL"

    # --- Formacje świecowe ---
    df['Hammer'] = ((high_data - low_data) > 3*(open_data - close_data)) & \
                   (((close_data - low_data)/(high_data - low_data + 0.001)) > 0.6)
    df['Doji'] = abs(close_data - open_data)/(high_data - low_data + 0.001) < 0.1
    df['Engulfing'] = ((close_data > open_data) & (close_data.shift(1) < open_data.shift(1)) & \
                       (close_data > open_data.shift(1))) | \
                      ((close_data < open_data) & (close_data.shift(1) > open_data.shift(1)) & \
                       (close_data < open_data.shift(1)))

    # --- Wykres świecowy ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(x=df.index,
                                        open=open_data,
                                        high=high_data,
                                        low=low_data,
                                        close=close_data,
                                        increasing_line_color='lime',
                                        decreasing_line_color='red',
                                        name="Świece"))
    for col_name, color in [('SMA20','orange'), ('SMA50','blue'), ('SMA200','purple'), ('EMA20','green'), ('EMA50','yellow')]:
        fig_candle.add_trace(go.Scatter(x=df.index, y=df[col_name], line=dict(color=color, width=2), name=col_name))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Panel Technical Analysis ---
    price = close_data.iloc[-1]
    change_24h = ((close_data.iloc[-1] - close_data.iloc[-2])/close_data.iloc[-2]*100) if len(close_data)>1 else 0
    rsi_value = df['RSI14'].iloc[-1]
    macd_value = df['MACD'].iloc[-1]
    volatility_30d = close_data.pct_change().dropna()[-30:].std() * 100
    signal_strength = 6
    signal = "Neutral"
    if rsi_value < 30 and close_data.iloc[-1] > df['SMA20'].iloc[-1]:
        signal = "Buy"; signal_strength=8
    elif rsi_value > 70 and close_data.iloc[-1] < df['SMA20'].iloc[-1]:
        signal = "Sell"; signal_strength=7

    st.markdown("### Technical Analysis")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Price (USD)", f"${price:.2f}", f"{change_24h:.2f}%")
    col2.metric("RSI (14)", f"{rsi_value:.2f}")
    col3.metric("MACD", f"{macd_value:.3f}")
    col4.metric("Volatility (30d)", f"{volatility_30d:.2f}%")
    col5.metric("Signal", f"{signal} ({signal_strength}/10)")

    if volatility_30d > 10:
        st.warning("High volatility detected – expect larger price swings ⚠️")

    # --- Ostatnie sygnały i wskaźniki ---
    st.subheader("Ostatnie sygnały Buy/Sell i wskaźniki")
    st.dataframe(df[['SMA20','SMA50','SMA200','EMA20','EMA50','RSI14','MACD','MACD_signal',
                     'BB_upper','BB_lower','ATR14','Stochastic','CCI20','Momentum5','OBV','ADX14',
                     'Signal','Hammer','Doji','Engulfing']].tail(20))
