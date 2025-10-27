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
    ticker = st.text_input("Wprowadź ticker (np. AAPL, TSLA):", "AAPL").upper()
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

    # Spłaszczenie MultiIndex jeśli istnieje
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    # Konwersja kolumn na float
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
        st.error(f"Brakuje wymaganych kolumn do wykresu świecowego")
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
    df['RSI'] = RSIIndicator(close_data, 14).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(high_data, low_data, close_data, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(high_data, low_data, close_data, 14).stoch()
    df['CCI'] = CCIIndicator(high_data, low_data, close_data, 20).cci()
    df['Momentum'] = MomentumIndicator(close_data, 5).momentum()
    df['OBV'] = OnBalanceVolumeIndicator(close_data, volume_data).on_balance_volume()
    df['ADX'] = ADXIndicator(high_data, low_data, close_data, 14).adx()

    # --- Sygnały BUY/SELL ---
    df['Signal'] = ""
    df.loc[(close_data > df['SMA20']) & (df['RSI'] < 70), 'Signal'] = "BUY"
    df.loc[(close_data < df['SMA20']) & (df['RSI'] > 30), 'Signal'] = "SELL"

    # --- Formacje świecowe ---
    df['Hammer'] = ((high_data - low_data) > 3*(open_data - close_data)) & \
                   (((close_data - low_data) / (0.001 + high_data - low_data)) > 0.6)
    df['Doji'] = abs(close_data - open_data) / (high_data - low_data + 0.001) < 0.1
    df['Engulfing'] = ((close_data > open_data) & (close_data.shift(1) < open_data.shift(1)) & \
                       (close_data > open_data.shift(1))) | \
                      ((close_data < open_data) & (close_data.shift(1) > open_data.shift(1)) & \
                       (close_data < open_data.shift(1)))

    # --- Wykres świecowy + wskaźniki ---
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
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='purple', width=2), name="SMA200"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue', width=2), name="EMA50"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
    fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

    st.plotly_chart(fig_candle, use_container_width=True)

    # --- Wolumen słupkowy ---
    if volume_data is not None:
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df.index, y=volume_data, name="Wolumen", marker_color='cyan'))
        fig_vol.update_layout(title="Wolumen", template="plotly_dark", height=200)
        st.plotly_chart(fig_vol, use_container_width=True)

    # --- Panel Technical Analysis ---
    st.subheader("Technical Analysis Panel")
    last_price = close_data.iloc[-1] if not close_data.empty else 0
    cols = st.columns(6)
    cols[0].metric("Price (USD)", f"${last_price:.2f}")
    cols[1].metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
    cols[2].metric("MACD", f"{df['MACD'].iloc[-1]:.3f}")
    cols[3].metric("ATR", f"{df['ATR'].iloc[-1]:.2f}")
    cols[4].metric("ADX", f"{df['ADX'].iloc[-1]:.2f}")
    cols[5].metric("Momentum", f"{df['Momentum'].iloc[-1]:.2f}")

    # --- Tabela ostatnich sygnałów ---
    st.subheader("Ostatnie sygnały BUY/SELL i formacje świecowe")
    st.dataframe(df[[close_col,'SMA20','SMA50','SMA200','EMA20','EMA50','RSI','MACD','BB_upper','BB_lower','ATR','Stochastic','CCI','Momentum','OBV','ADX','Signal','Hammer','Doji','Engulfing']].tail(20))
