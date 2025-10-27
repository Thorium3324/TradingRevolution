import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, CCIIndicator, MomentumIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def akcje_tab():
    st.subheader("Zakładka Akcje - TradingRevolution Ultimate")

    # --- Dane wejściowe ---
    ticker = st.text_input("Ticker akcji (np. AAPL, TSLA):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"])

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

    # --- Konwersja MultiIndex na zwykłe kolumny ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    # --- Konwersja kolumn na float ---
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

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
        st.error(f"Brakuje wymaganych kolumn: Open/High/Low/Close")
        return

    o, h, l, c = df[open_col], df[high_col], df[low_col], df[close_col]
    v = df[volume_col] if volume_col else pd.Series([0]*len(df), index=df.index)

    # --- Wskaźniki techniczne ---
    df['SMA20'] = SMAIndicator(c, 20).sma_indicator()
    df['SMA50'] = SMAIndicator(c, 50).sma_indicator()
    df['SMA200'] = SMAIndicator(c, 200).sma_indicator()
    df['EMA20'] = EMAIndicator(c, 20).ema_indicator()
    df['EMA50'] = EMAIndicator(c, 50).ema_indicator()
    df['RSI'] = RSIIndicator(c, 14).rsi()
    macd = MACD(c)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['BB_upper'] = BollingerBands(c).bollinger_hband()
    df['BB_lower'] = BollingerBands(c).bollinger_lband()
    df['ATR'] = AverageTrueRange(h, l, c, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(h, l, c, 14).stoch()
    df['CCI'] = CCIIndicator(h, l, c, 20).cci()
    df['Momentum5'] = MomentumIndicator(c, 5).momentum()
    df['OBV'] = OnBalanceVolumeIndicator(c, v).on_balance_volume()
    df['ADX'] = ADXIndicator(h, l, c, 14).adx()

    # --- Sygnały Buy/Sell ---
    df['Signal'] = ""
    df.loc[(c > df['SMA20']) & (df['RSI'] < 70), 'Signal'] = "BUY"
    df.loc[(c < df['SMA20']) & (df['RSI'] > 30), 'Signal'] = "SELL"

    # --- Wykres świecowy + wskaźniki ---
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(x=df.index, open=o, high=h, low=l, close=c,
                                        increasing_line_color='lime', decreasing_line_color='red', name="Świece"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='yellow', width=2), name="SMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='pink', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue', width=2), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark",
                             xaxis_rangeslider_visible=False, height=600)

    # --- RSI wykres ---
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title="RSI (14)", template="plotly_dark", height=250)

    # --- MACD wykres ---
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='cyan', width=2), name="MACD"))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], line=dict(color='yellow', width=2), name="MACD Signal"))
    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)

    # --- Wolumen ---
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(x=df.index, y=v, name="Wolumen", marker_color='blue'))
    fig_vol.update_layout(title="Wolumen", template="plotly_dark", height=200)

    # --- Wyświetlenie wykresów ---
    st.plotly_chart(fig_candle, use_container_width=True)
    st.plotly_chart(fig_rsi, use_container_width=True)
    st.plotly_chart(fig_macd, use_container_width=True)
    st.plotly_chart(fig_vol, use_container_width=True)

    # --- Panel Technical Analysis ---
    price = c[-1]
    change_1d = ((c[-1]-c[-2])/c[-2]*100) if len(c) > 1 else 0
    rsi_val = df['RSI'][-1]
    macd_val = df['MACD'][-1]
    volatility_30d = c.pct_change().dropna()[-30:].std() * 100
    signal_strength = 6
    signal = "Neutral"
    if rsi_val < 30 and c[-1] > df['SMA20'][-1]:
        signal = "Buy"
        signal_strength = 8
    elif rsi_val > 70 and c[-1] < df['
