# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def financial_analysis(df, ticker):
    results = {}
    close_col = 'Close'
    if close_col not in df.columns or df[close_col].empty:
        return results, df

    # =========================
    # Zaawansowane wskaźniki techniczne
    # =========================
    df['SMA20'] = SMAIndicator(df[close_col], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df[close_col], 50).sma_indicator()
    df['SMA200'] = SMAIndicator(df[close_col], 200).sma_indicator()

    df['EMA20'] = EMAIndicator(df[close_col], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df[close_col], 50).ema_indicator()

    bb = BollingerBands(df[close_col], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    results['BB_upper'] = df['BB_upper'].iloc[-1]
    results['BB_lower'] = df['BB_lower'].iloc[-1]

    atr = AverageTrueRange(df['High'], df['Low'], df[close_col], window=14)
    df['ATR'] = atr.average_true_range()
    results['ATR'] = df['ATR'].iloc[-1]

    rsi = RSIIndicator(df[close_col], window=14)
    df['RSI'] = rsi.rsi()
    results['RSI'] = df['RSI'].iloc[-1]

    stoch = StochasticOscillator(df['High'], df['Low'], df[close_col], window=14, smooth_window=3)
    df['Stoch'] = stoch.stoch()
    results['Stochastic'] = df['Stoch'].iloc[-1]

    cci = CCIIndicator(df['High'], df['Low'], df[close_col], window=20)
    df['CCI'] = cci.cci()
    results['CCI'] = df['CCI'].iloc[-1]

    macd = MACD(df[close_col])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    results['MACD'] = df['MACD'].iloc[-1]

    df['Momentum'] = df[close_col].diff(5)
    results['Momentum'] = df['Momentum'].iloc[-1]

    obv = OnBalanceVolumeIndicator(df[close_col], df['Volume'])
    df['OBV'] = obv.on_balance_volume()
    results['OBV'] = df['OBV'].iloc[-1]

    # =========================
    # Analizy dodatkowe
    # =========================
    df['returns'] = df[close_col].pct_change()
    results['Volatility_30d'] = df['returns'].rolling(window=30).std().iloc[-1] * np.sqrt(252)

    # =========================
    # Analizy fundamentalne
    # =========================
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        results['PE'] = info.get('trailingPE', '-')
        results['EPS'] = info.get('trailingEps', '-')
        results['MarketCap'] = info.get('marketCap', '-')
        results['DividendYield'] = info.get('dividendYield', '-')
        results['Beta'] = info.get('beta', '-')
    except:
        results['PE'] = results['EPS'] = results['MarketCap'] = results['DividendYield'] = results['Beta'] = '-'

    # =========================
    # Sygnał trendu i ostrzeżenia
    # =========================
    signal = "Neutral"
    strength = 0
    warnings = []

    # Trend na SMA
    if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
        signal = "Kupno"
        strength += 3
    if df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
        signal = "Sprzedaż"
        strength += 3

    # RSI
    if results['RSI'] < 30:
        signal = "Kupno"
        strength += 2
        warnings.append("RSI < 30 - możliwe wyprzedanie")
    elif results['RSI'] > 70:
        signal = "Sprzedaż"
        strength += 2
        warnings.append("RSI > 70 - możliwe wykupienie")

    # MACD
    if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
        strength += 1
    elif df['MACD'].iloc[-1] < df['MACD_signal'].iloc[-1]:
        strength += 1

    # ATR - wysoka zmienność
    if results['ATR'] > df[close_col].mean() * 0.02:
        warnings.append("Wysoka zmienność – spodziewaj się większych ruchów cen ⚠️")

    results['Signal'] = signal
    results['Signal_Strength'] = strength
    results['Warnings'] = warnings

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
        st.warning("Brak danych dla wybranego symbolu.")
        return

    df.reset_index(inplace=True)
    for col in ['Open','High','Low','Close','Volume']:
        if col not in df.columns:
            df[col] = np.nan

    fin_results, df = financial_analysis(df, ticker)

    # =========================
    # Wyświetlanie metryk
    # =========================
    st.subheader(f"Analiza techniczna i fundamentalna - {ticker}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}" if not df['Close'].isna().all() else "Brak")
    col1.metric("SMA20", f"{df['SMA20'].iloc[-1]:.2f}" if 'SMA20' in df else "-")
    col1.metric("SMA50", f"{df['SMA50'].iloc[-1]:.2f}" if 'SMA50' in df else "-")
    col2.metric("RSI(14)", f"{fin_results.get('RSI',0):.2f}")
    col2.metric("MACD", f"{fin_results.get('MACD',0):.2f}")
    col2.metric("Momentum", f"{fin_results.get('Momentum',0):.2f}")
    col3.metric("ATR", f"{fin_results.get('ATR',0):.2f}")
    col3.metric("Volatility 30d", f"{fin_results.get('Volatility_30d',0)*100:.2f}%")
    col3.metric("OBV", f"{fin_results.get('OBV',0):.0f}")

    st.subheader("📊 Analizy fundamentalne")
    colf1, colf2, colf3 = st.columns(3)
    colf1.metric("P/E", fin_results.get('PE','-'))
    colf1.metric("EPS", fin_results.get('EPS','-'))
    colf2.metric("Market Cap", fin_results.get('MarketCap','-'))
    colf2.metric("Dividend Yield", fin_results.get('DividendYield','-'))
    colf3.metric("Beta", fin_results.get('Beta','-'))
    colf3.metric("Trend Signal", f"{fin_results.get('Signal','Neutral')} ({fin_results.get('Signal_Strength',0)}/10)")

    if fin_results.get('Warnings'):
        st.warning(" | ".join(fin_results['Warnings']))

    # =========================
    # Wykres świecowy
    # =========================
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    )])
    fig.update_layout(title=f"Wykres świecowy - {ticker}",
                      xaxis_title="Data",
                      yaxis_title="Cena (USD)",
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
