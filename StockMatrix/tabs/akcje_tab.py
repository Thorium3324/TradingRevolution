# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator

# Funkcja pobierania danych z cache (1h)
@st.cache_data(ttl=3600)
def get_stock_data(symbol="AAPL"):
    try:
        df = yf.download(symbol, period="1y", interval="1d")
        if df.empty:
            return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

# Dodawanie wskaźników technicznych
def add_technical_indicators(df):
    df = df.copy()
    df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    return df

# Zakładka Akcje
def akcje_tab():
    st.header("📈 Zakładka Akcje")

    ticker = st.text_input("Wpisz symbol akcji (np. AAPL):", "AAPL")
    if not ticker:
        st.info("Wpisz symbol akcji, aby wyświetlić dane.")
        return

    if st.button("Pobierz dane"):
        df = get_stock_data(ticker.upper())
        if df is None:
            st.warning("Nie znaleziono danych dla wybranego symbolu.")
            return

        # Dodaj wskaźniki
        df = add_technical_indicators(df)

        # Pokaz metryki
        st.subheader("Techniczne informacje")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cena (USD)", f"${df['Close'].iloc[-1]:.2f}")
        col2.metric("SMA20", f"${df['SMA20'].iloc[-1]:.2f}")
        col3.metric("SMA50", f"${df['SMA50'].iloc[-1]:.2f}")
        col4.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

        # Wykres świecowy z wolumenem
        st.subheader(f"Wykres świecowy dla {ticker.upper()}")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=ticker.upper()
        ))
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Wolumen",
            marker_color='blue',
            yaxis='y2'
        ))
        fig.update_layout(
            yaxis=dict(title='Cena'),
            yaxis2=dict(title='Wolumen', overlaying='y', side='right', showgrid=False, position=0.15),
            xaxis_rangeslider_visible=False,
            height=600,
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Ostatnie dane
        st.subheader("Ostatnie dane")
        st.dataframe(df.tail(10))
