# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import SMAIndicator, CCIIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def financial_analysis(df, ticker):
    results = {}
    close_col = 'Close'
    if close_col not in df.columns:
        return results, df

    # SMA
    df['SMA20'] = SMAIndicator(df[close_col], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df[close_col], 50).sma_indicator()

    # Bollinger Bands
    bb = BollingerBands(df[close_col], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    results['BB_upper'] = df['BB_upper'].iloc[-1]
    results['BB_lower'] = df['BB_lower'].iloc[-1]

    # ATR
    atr = AverageTrueRange(df['High'], df['Low'], df[close_col], window=14)
    df['ATR'] = atr.average_true_range()
    results['ATR'] = df['ATR'].iloc[-1]

    # RSI
    rsi = RSIIndicator(df[close_col], window=14)
    df['RSI'] = rsi.rsi()
    results['RSI'] = df['RSI'].iloc[-1]

    # Stochastic Oscillator
    stoch = StochasticOscillator(df['High'], df['Low'], df[close_col], window=14, smooth_window=3)
    df['Stoch'] = stoch.stoch()
    results['Stochastic'] = df['Stoch'].iloc[-1]

    # CCI
    cci = CCIIndicator(df['High'], df['Low'], df[close_col], window=20)
    df['CCI'] = cci.cci()
    results['CCI'] = df['CCI'].iloc[-1]

    # MACD
    macd = MACD(df[close_col])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    results['MACD'] = df['MACD'].iloc[-1]

    # Momentum
    df['Momentum'] = df[close_col].diff(5)
    results['Momentum'] = df['Momentum'].iloc[-1]

    # OBV
    obv = OnBalanceVolumeIndicator(df[close_col], df['Volume'])
    df['OBV'] = obv.on_balance_volume()
    results['OBV'] = df['OBV'].iloc[-1]

    # Volatility 30d
    df['returns'] = df[close_col].pct_change()
    results['Volatility_30d'] = df['returns'].rolling(window=30).std().iloc[-1] * np.sqrt(252)

    # Fundamentalne
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        results['PE'] = info.get('trailingPE', None)
        results['EPS'] = info.get('trailingEps', None)
        results['MarketCap'] = info.get('marketCap', None)
        results['DividendYield'] = info.get('dividendYield', None)
        results['Beta'] = info.get('beta', None)
    except:
        pass

    return results, df

def akcje_tab():
    st.header("📈 Akcje")

    ticker = st.text_input("Wpisz ticker akcji (np. AAPL, TSLA)", value="AAPL").upper()
    if not ticker:
        st.warning("Wpisz ticker akcji aby rozpocząć")
        return

    try:
        df = yf.download(ticker, period="6mo", interval="1d")
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return

    if df.empty:
        st.warning("Nie znaleziono danych dla wybranego symbolu.")
        return

    df.reset_index(inplace=True)

    # Upewnij się, że kolumny istnieją
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # Techniczne i finansowe analizy
    fin_results, df = financial_analysis(df, ticker)

    # Wyświetlanie metryk
    st.subheader(f"Technical Analysis - {ticker}")
    col1, col2, col3 = st.columns(3)

    col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}" if not df['Close'].isna().all() else "Brak")
    col1.metric("SMA20", f"{df['SMA20'].iloc[-1]:.2f}" if 'SMA20' in df else "Brak")
    col1.metric("SMA50", f"{df['SMA50'].iloc[-1]:.2f}" if 'SMA50' in df else "Brak")

    col2.metric("RSI(14)", f"{fin_results.get('RSI',0):.2f}")
    col2.metric("MACD", f"{fin_results.get('MACD',0):.2f}")
    col2.metric("Momentum", f"{fin_results.get('Momentum',0):.2f}")

    col3.metric("ATR", f"{fin_results.get('ATR',0):.2f}")
    col3.metric("Volatility 30d", f"{fin_results.get('Volatility_30d',0)*100:.2f}%")
    col3.metric("OBV", f"{fin_results.get('OBV',0):.0f}")

    # Wykres świecowy
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         name=ticker)])
    fig.update_layout(title=f"Wykres świecowy - {ticker}", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Analiza finansowa
    if fin_results:
        st.subheader("Analiza finansowa")
        st.write(f"P/E: {fin_results.get('PE','Brak')}")
        st.write(f"EPS: {fin_results.get('EPS','Brak')}")
        st.write(f"Market Cap: {fin_results.get('MarketCap','Brak')}")
        st.write(f"Dividend Yield: {fin_results.get('DividendYield','Brak')}")
        st.write(f"Beta: {fin_results.get('Beta','Brak')}")
