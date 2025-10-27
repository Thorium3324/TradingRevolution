import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator, MomentumIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from datetime import datetime, timedelta
import plotly.graph_objects as go

# =========================
# Funkcja pobierania danych
# =========================
def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval)
        if df.empty:
            return None
        df = df.reset_index()
        df.rename(columns=lambda x: x.replace(" ", ""), inplace=True)
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

# =========================
# Funkcja dodająca wskaźniki techniczne
# =========================
def add_technical_indicators(df):
    df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
    df['SMA200'] = SMAIndicator(df['Close'], 200).sma_indicator()
    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df['Close'], 50).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(df['Close'], 20, 2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
    df['Stoch'] = StochasticOscillator(df['High'], df['Low'], df['Close'], 14, 3).stoch()
    df['CCI'] = pd.Series(np.nan)  # Możesz dodać obliczenia CCI jeśli chcesz
    df['Momentum'] = MomentumIndicator(df['Close'], 5).momentum()
    df['OBV'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    return df

# =========================
# Funkcja analiz fundamentalnych
# =========================
def fundamental_analysis(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    results = {
        "P/E": info.get("trailingPE", 0),
        "EPS": info.get("trailingEps", 0),
        "MarketCap": info.get("marketCap", 0),
        "DividendYield": info.get("dividendYield", 0),
        "Beta": info.get("beta", 0),
        "Volatility_30d": 0.0  # Można obliczyć z cen historycznych
    }
    return results

# =========================
# Zakładka Akcje
# =========================
def akcje_tab():
    st.title("TradingRevolution - Akcje")
    ticker = st.text_input("Wpisz symbol akcji (np. AAPL, TSLA)", "AAPL").upper()

    df = get_stock_data(ticker)
    if df is None or df.empty:
        st.warning("Nie znaleziono danych dla wybranego symbolu.")
        return

    df = add_technical_indicators(df)
    fin_results = fundamental_analysis(ticker)

    # =========================
    # Podstawowe metryki
    # =========================
    st.subheader(f"Podstawowe dane - {ticker}")
    col1, col2, col3, col4 = st.columns(4)
    last_close = df['Close'].iloc[-1]
    col1.metric("Cena (USD)", f"${last_close:.2f}")
    col2.metric("Zmienność 30d", f"{fin_results['Volatility_30d']*100:.2f}%")
    col3.metric("P/E", f"{fin_results['P/E']:.2f}")
    col4.metric("EPS", f"{fin_results['EPS']:.2f}")

    # =========================
    # Zaawansowane wskaźniki techniczne
    # =========================
    st.subheader(f"Zaawansowane wskaźniki techniczne - {ticker}")
    col1, col2, col3, col4 = st.columns(4)

    # Kolumna 1
    col1.metric("SMA20", f"{df['SMA20'].iloc[-1]:.2f}")
    col1.metric("SMA50", f"{df['SMA50'].iloc[-1]:.2f}")
    col1.metric("SMA200", f"{df['SMA200'].iloc[-1]:.2f}")
    col1.metric("EMA20", f"{df['EMA20'].iloc[-1]:.2f}")

    # Kolumna 2
    col2.metric("EMA50", f"{df['EMA50'].iloc[-1]:.2f}")
    col2.metric("RSI(14)", f"{df['RSI'].iloc[-1]:.2f}")
    col2.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")
    col2.metric("MACD Signal", f"{df['MACD_signal'].iloc[-1]:.2f}")

    # Kolumna 3
    col3.metric("Bollinger Upper", f"{df['BB_upper'].iloc[-1]:.2f}")
    col3.metric("Bollinger Lower", f"{df['BB_lower'].iloc[-1]:.2f}")
    col3.metric("ATR(14)", f"{df['ATR'].iloc[-1]:.2f}")
    col3.metric("Stochastic", f"{df['Stoch'].iloc[-1]:.2f}")

    # Kolumna 4
    col4.metric("CCI(20)", f"{df['CCI'].iloc[-1] if 'CCI' in df else 0:.2f}")
    col4.metric("Momentum(5)", f"{df['Momentum'].iloc[-1]:.2f}")
    col4.metric("OBV", f"{df['OBV'].iloc[-1]:.0f}")

    # =========================
    # Wykres świecowy
    # =========================
    st.subheader(f"Wykres świecowy - {ticker}")
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
