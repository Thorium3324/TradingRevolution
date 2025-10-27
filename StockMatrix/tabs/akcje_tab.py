# tabs/akcje_tab.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator

def akcje_tab():
    st.title("📈 Analiza Akcji")

    ticker = st.text_input("Podaj ticker akcji:", "AAPL").upper()
    if not ticker:
        st.warning("Podaj ticker akcji, aby rozpocząć analizę.")
        return

    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    except Exception as e:
        st.error(f"❌ Błąd pobierania danych: {e}")
        return

    if df.empty:
        st.error(f"❌ Nie udało się pobrać danych dla {ticker}")
        return

    df = df.reset_index()

    # Wymagane kolumny
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    existing_cols = []

    for col in required_cols:
        if col in df.columns:
            # Jeśli kolumna jest DataFrame (multiindex), bierzemy pierwszą kolumnę
            if isinstance(df[col], pd.DataFrame):
                df[col] = df[col].iloc[:, 0]
            # Spłaszczamy do 1-wymiarowej serii i konwertujemy do numeric
            df[col] = pd.to_numeric(pd.Series(df[col].values.flatten()), errors='coerce')
            existing_cols.append(col)

    if not existing_cols:
        st.error("❌ Brak wymaganych kolumn w danych. Spróbuj inny ticker.")
        return

    # Dropna po istniejących kolumnach
    df = df.dropna(subset=existing_cols)
    if df.empty:
        st.error("❌ Dane po konwersji są puste.")
        return

    # Kolumna Close do wyświetlania
    close_col = 'Close' if 'Close' in df.columns else existing_cols[-1]

    # Metryki
    col1, col2, col3 = st.columns(3)
    col1.metric("Cena (USD)", f"${df[close_col].iloc[-1]:.2f}")
    col2.metric("Zmiana 24h", f"{(df[close_col].pct_change().iloc[-1]*100):.2f}%" if len(df) > 1 else "Brak danych")

    # Wskaźniki techniczne
    if 'Close' in df.columns:
        df['SMA20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['EMA20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
        df['RSI14'] = RSIIndicator(df['Close'], window=14).rsi()
        col3.metric("RSI (14)", f"{df['RSI14'].iloc[-1]:.2f}" if not df['RSI14'].isna().all() else "Brak danych")

    # Wykres świecowy
    st.markdown("### Wykres świecowy z SMA/EMA")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'] if 'Open' in df.columns else df[close_col],
        high=df['High'] if 'High' in df.columns else df[close_col],
        low=df['Low'] if 'Low' in df.columns else df[close_col],
        close=df[close_col],
        name=ticker
    ))
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA20'], mode='lines', name='SMA20', line=dict(color='orange')))
    if 'EMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], mode='lines', name='EMA20', line=dict(color='green')))
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Wolumen
    if 'Volume' in df.columns:
        st.markdown("### Wolumen")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name="Wolumen", marker_color='blue'))
        fig_vol.update_layout(template="plotly_dark", height=250)
        st.plotly_chart(fig_vol, use_container_width=True)

    # Analiza techniczna
    st.markdown("### Analiza techniczna")
    signal = "Neutral"
    strength = 5
    rsi = df['RSI14'].iloc[-1] if 'RSI14' in df.columns and not df['RSI14'].isna().all() else None

    if rsi is not None:
        if rsi < 30:
            signal = "Kupuj"
            strength = 8
        elif rsi > 70:
            signal = "Sprzedaj"
            strength = 8

    st.info(f"**Sygnał:** {signal} | **Siła:** {strength}/10 | **RSI:** {rsi:.2f}" if rsi is not None else "Brak danych RSI")

    # Volatility 30-dniowa
    if 'Close' in df.columns:
        df['returns'] = df['Close'].pct_change()
        volatility = df['returns'].rolling(30).std().iloc[-1]*100 if not df['returns'].isna().all() else None
        st.write(f"📊 **Volatility (30 dni):** {volatility:.2f}%" if volatility is not None else "Brak danych dla zmienności")
