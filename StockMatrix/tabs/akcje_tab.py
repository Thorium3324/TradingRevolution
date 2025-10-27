import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def akcje_tab():
    st.title("📈 Zakładka Akcje – TradingRevolution Ultimate")

    # --- Ustawienia wejściowe ---
    ticker = st.text_input("Podaj symbol akcji (np. AAPL, TSLA, MSFT):", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk", "1mo"])

    sma_short = st.sidebar.slider("SMA krótkoterminowa (20)", 5, 100, 20)
    sma_mid = st.sidebar.slider("SMA średnioterminowa (50)", 10, 200, 50)
    sma_long = st.sidebar.slider("SMA długoterminowa (200)", 50, 400, 200)
    ema_short = st.sidebar.slider("EMA (20)", 5, 100, 20)
    rsi_period = st.sidebar.slider("RSI (okres)", 5, 50, 14)
    stochastic_period = st.sidebar.slider("Stochastic (okres)", 5, 50, 14)
    atr_period = st.sidebar.slider("ATR (okres)", 5, 50, 14)
    cci_period = st.sidebar.slider("CCI (okres)", 5, 50, 20)
    momentum_period = st.sidebar.slider("Momentum (dni)", 3, 30, 5)

    # --- Pobranie danych ---
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return

    if df.empty:
        st.warning("Brak danych dla wybranego symbolu.")
        return

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # --- Wskaźniki techniczne ---
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    df["SMA20"] = SMAIndicator(close, sma_short).sma_indicator()
    df["SMA50"] = SMAIndicator(close, sma_mid).sma_indicator()
    df["SMA200"] = SMAIndicator(close, sma_long).sma_indicator()
    df["EMA20"] = EMAIndicator(close, ema_short).ema_indicator()
    df["RSI"] = RSIIndicator(close, rsi_period).rsi()
    df["MACD"] = MACD(close).macd()
    df["MACD_signal"] = MACD(close).macd_signal()
    df["BB_upper"] = BollingerBands(close).bollinger_hband()
    df["BB_lower"] = BollingerBands(close).bollinger_lband()
    df["ATR"] = AverageTrueRange(high, low, close, atr_period).average_true_range()
    df["Stochastic"] = StochasticOscillator(high, low, close, stochastic_period).stoch()
    df["CCI"] = CCIIndicator(high, low, close, cci_period).cci()
    df["Momentum"] = close.pct_change(momentum_period) * 100
    df["OBV"] = OnBalanceVolumeIndicator(close, volume).on_balance_volume()

    # --- Sygnały trendu ---
    last_rsi = df["RSI"].iloc[-1]
    last_macd = df["MACD"].iloc[-1]
    last_close = close.iloc[-1]
    last_sma20 = df["SMA20"].iloc[-1]

    if last_rsi < 30 and last_close > last_sma20:
        signal = "Kupno ✅"
    elif last_rsi > 70 and last_close < last_sma20:
        signal = "Sprzedaż ⚠️"
    else:
        signal = "Neutralny ⚪"

    # --- Wykres świecowy ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=high, low=low, close=close,
        increasing_line_color="lime", decreasing_line_color="red", name="Cena"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], line=dict(color="orange", width=2), name="SMA 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], line=dict(color="blue", width=2), name="SMA 50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], line=dict(color="purple", width=2), name="SMA 200"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], line=dict(color="gray", width=1, dash="dot"), name="BB Upper"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], line=dict(color="gray", width=1, dash="dot"), name="BB Lower"))
    fig.update_layout(title=f"{ticker} – Wykres świecowy", xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- RSI ---
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="magenta", width=2), name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title="RSI (14)", template="plotly_dark", height=250)
    st.plotly_chart(fig_rsi, use_container_width=True)

    # --- MACD ---
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], line=dict(color="cyan", width=2), name="MACD"))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], line=dict(color="yellow", width=2), name="Signal"))
    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)
    st.plotly_chart(fig_macd, use_container_width=True)

    # --- Panel metryk ---
    price = close.iloc[-1]
    change_1d = close.pct_change().iloc[-1] * 100
    volatility_30d = close.pct_change().dropna()[-30:].std() * 100

    st.markdown("### 📊 Analiza Techniczna")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cena (USD)", f"${price:.2f}", f"{change_1d:.2f}%")
    c2.metric("RSI", f"{last_rsi:.2f}")
    c3.metric("MACD", f"{last_macd:.2f}")
    c4.metric("Zmienność (30d)", f"{volatility_30d:.2f}%")
    c5.metric("Sygnał", signal)

    # --- Tabela wskaźników ---
    st.subheader("📋 Kluczowe wskaźniki techniczne")
    st.dataframe(df[[
        "Close", "SMA20", "SMA50", "SMA200", "EMA20", "RSI", "MACD", "MACD_signal",
        "BB_upper", "BB_lower", "ATR", "Stochastic", "CCI", "Momentum", "OBV"
    ]].tail(20))
