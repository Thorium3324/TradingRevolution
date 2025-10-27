import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def akcje_tab():
    st.title("📊 Analiza akcji – Trading Revolution")

    ticker = st.text_input("Wpisz symbol akcji:", "AAPL")
    period = st.selectbox("Okres danych:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
    interval = st.selectbox("Interwał:", ["1d", "1wk", "1mo"])

    df = get_stock_data(ticker, period, interval)

    if df.empty:
        st.error("❌ Nie udało się pobrać danych.")
        return

    df.dropna(inplace=True)

    # Obliczenia wskaźników
    df["RSI"] = compute_rsi(df["Close"])
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    macd_line, signal_line, hist = compute_macd(df["Close"])
    df["MACD_Line"] = macd_line
    df["Signal_Line"] = signal_line
    df["Hist"] = hist

    # Wykres świecowy
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA 20", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA 50", line=dict(color="orange")))
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Wskaźniki techniczne
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}")
    col2.metric("24h Zmiana", f"{((df['Close'].iloc[-1]/df['Close'].iloc[-2]-1)*100):.2f}%")
    col3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
    col4.metric("MACD", f"{df['MACD_Line'].iloc[-1]:.3f}")

    st.subheader("📉 RSI i MACD")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="cyan")))
    fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
    fig_rsi.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_rsi, use_container_width=True)

    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD_Line"], name="MACD", line=dict(color="yellow")))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"], name="Signal", line=dict(color="magenta")))
    fig_macd.add_trace(go.Bar(x=df.index, y=df["Hist"], name="Histogram", marker_color="gray"))
    fig_macd.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_macd, use_container_width=True)

# --- Funkcje pomocnicze ---
def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df = df.reset_index().set_index("Date")
        return df
    except:
        return pd.DataFrame()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist
