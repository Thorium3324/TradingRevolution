# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator, MomentumIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import CCIIndicator

def get_stock_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period)
        if df.empty:
            st.warning(f"Brak danych dla symbolu: {symbol}")
            return None
        df.reset_index(inplace=True)
        df.columns = [col.replace(" ", "_") for col in df.columns]  # unikamy spacji
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

def add_technical_indicators(df):
    # SMA
    if 'Close' in df:
        df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
        df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
        df['SMA200'] = SMAIndicator(df['Close'], 200).sma_indicator()
        df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
        df['EMA50'] = EMAIndicator(df['Close'], 50).ema_indicator()
        df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['Momentum5'] = MomentumIndicator(df['Close'], 5).momentum()
    
    if all(col in df for col in ['High', 'Low', 'Close']):
        df['ATR14'] = AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
        df['Bollinger_High'] = BollingerBands(df['Close'], 20, 2).bollinger_hband()
        df['Bollinger_Low'] = BollingerBands(df['Close'], 20, 2).bollinger_lband()
        df['CCI20'] = CCIIndicator(df['High'], df['Low'], df['Close'], 20).cci()
        df['Stochastic'] = StochasticOscillator(df['High'], df['Low'], df['Close'], 14).stoch()
    
    if all(col in df for col in ['Close', 'Volume']):
        df['OBV'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    
    return df

def akcje_tab():
    st.title("Zakładka Akcje – TradingRevolution")
    symbol = st.text_input("Wpisz ticker akcji (np. AAPL, TSLA, MSFT):", value="AAPL")
    
    df = get_stock_data(symbol)
    if df is None or df.empty:
        st.warning("Nie znaleziono danych lub symbol jest niepoprawny.")
        return

    df = add_technical_indicators(df)
    
    # Wskaźniki metryki
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Cena (USD)", f"{df['Close'].iloc[-1]:.2f}" if 'Close' in df else "N/A")
    col2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}" if 'RSI' in df else "N/A")
    col3.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}" if 'MACD' in df else "N/A")
    
    # Wyświetlenie wykresu świecowego
    import plotly.graph_objects as go
    if all(col in df for col in ['Open', 'High', 'Low', 'Close']):
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol
        )])
        fig.update_layout(title=f"Wykres świecowy: {symbol}", xaxis_title="Data", yaxis_title="Cena USD")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Brakuje kolumn do wykresu świecowego.")
    
    # Wyświetlenie wszystkich wskaźników
    st.subheader("Wskaźniki techniczne")
    indicators = ['SMA20','SMA50','SMA200','EMA20','EMA50','RSI','MACD','MACD_signal',
                  'ATR14','Bollinger_High','Bollinger_Low','CCI20','Stochastic','Momentum5','OBV']
    indicator_data = {i: df[i].iloc[-1] if i in df else "N/A" for i in indicators}
    st.write(indicator_data)
    
    # Analizy fundamentalne (jeśli dostępne w yf.Ticker)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        st.subheader("Analiza fundamentalna")
        st.metric("P/E", info.get("trailingPE", "N/A"))
        st.metric("EPS", info.get("trailingEps", "N/A"))
        st.metric("Market Cap", info.get("marketCap", "N/A"))
        st.metric("Dividend Yield", info.get("dividendYield", "N/A"))
        st.metric("Beta", info.get("beta", "N/A"))
    except Exception as e:
        st.warning(f"Nie udało się pobrać danych fundamentalnych: {e}")
    
    # Dodatkowe analizy
    st.subheader("Analizy dodatkowe")
    if 'Close' in df:
        vol30 = df['Close'].pct_change().rolling(30).std().iloc[-1]*100
        st.metric("Volatility 30d", f"{vol30:.2f}%")
    
    # Sygnalizacja trendu
    trend_signal = "Neutral"
    if 'SMA20' in df and 'SMA50' in df:
        if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
            trend_signal = "Kupno"
        elif df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
            trend_signal = "Sprzedaż"
    st.metric("Signal Trend", trend_signal)
