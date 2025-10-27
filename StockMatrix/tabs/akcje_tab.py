# tabs/akcje_tab.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator

# Funkcja do pobrania przykładowych danych (zastąp własnym fetcherem)
def get_stock_data(symbol="AAPL"):
    try:
        df = pd.read_csv(f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1=0&period2=9999999999&interval=1d&events=history")
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        # Wybieramy podstawowe kolumny
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

# Dodaj wskaźniki techniczne
def add_technical_indicators(df):
    df = df.copy()
    df['SMA20'] = SMAIndicator(df['Close'], 20).sma_indicator()
    df['SMA50'] = SMAIndicator(df['Close'], 50).sma_indicator()
    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    return df

# Główna funkcja zakładki Akcje
def akcje_tab():
    st.header("📈 Zakładka Akcje")
    ticker = st.text_input("Wpisz symbol akcji (np. AAPL):", "AAPL")

    if not ticker:
        st.info("Wpisz symbol akcji, aby wyświetlić dane.")
        return

    df = get_stock_data(ticker)
    if df is None or df.empty:
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
    st.subheader(f"Wykres świecowy dla {ticker}")
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    ))

    # Wolumen jako słupki
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name="Wolumen",
        marker_color='blue',
        yaxis='y2'
    ))

    # Dodanie osi wolumenu
    fig.update_layout(
        yaxis=dict(title='Cena'),
        yaxis2=dict(title='Wolumen', overlaying='y', side='right', showgrid=False, position=0.15),
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Pokaz ostatnie wiersze danych
    st.subheader("Ostatnie dane")
    st.dataframe(df.tail(10))
