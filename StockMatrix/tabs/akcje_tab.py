import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator

def akcje_tab():
    st.title("📈 Analiza Akcji")
    
    ticker = st.text_input("Podaj ticker akcji:", "AAPL").upper()
    
    # Pobranie danych
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    except Exception as e:
        st.error(f"❌ Błąd pobierania danych: {e}")
        return
    
    if df.empty:
        st.error(f"❌ Nie udało się pobrać danych dla {ticker}")
        return
    
    # Reset index
    df = df.reset_index()
    
    # Konwersja kolumn na numeryczne
    required_cols = ['Open','High','Low','Close','Volume']
    for col in required_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sprawdzenie obecności kolumn
    for col in ['Open','High','Low','Close','Volume']:
        if col not in df.columns:
            st.error(f"❌ Brakuje kolumny {col} w danych dla {ticker}")
            return
    
    # Dropna dla bezpieczeństwa
    df = df.dropna(subset=['Open','High','Low','Close'])
    if df.empty:
        st.error("❌ Dane po konwersji są puste.")
        return
    
    # Kolumny
    open_col = 'Open'
    high_col = 'High'
    low_col = 'Low'
    close_col = 'Close'
    volume_col = 'Volume'
    
    # Podstawowe informacje
    col1, col2, col3 = st.columns(3)
    try:
        col1.metric("Cena (USD)", f"${df[close_col].iloc[-1]:.2f}")
        col2.metric("Zmiana 24h", f"{df[close_col].pct_change().iloc[-1]*100:.2f}%")
    except Exception as e:
        st.warning(f"❌ Nie udało się wyświetlić ceny: {e}")
        return
    
    # Wskaźniki techniczne
    df['SMA20'] = SMAIndicator(df[close_col], window=20).sma_indicator()
    df['EMA20'] = EMAIndicator(df[close_col], window=20).ema_indicator()
    df['RSI'] = RSIIndicator(df[close_col], window=14).rsi()
    
    col3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}" if not df['RSI'].isna().all() else "Brak danych")
    
    # Wykres świecowy
    st.markdown("### Wykres świecowy z SMA i EMA")
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        name=ticker
    )])
    
    # SMA i EMA
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA20'], mode='lines', name='SMA20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], mode='lines', name='EMA20', line=dict(color='green')))
    
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Wykres wolumenu
    st.markdown("### Wolumen")
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(x=df['Date'], y=df[volume_col], name="Wolumen", marker_color='blue'))
    fig_vol.update_layout(template="plotly_dark", height=250)
    st.plotly_chart(fig_vol, use_container_width=True)
    
    # Analiza techniczna
    st.markdown("### Analiza techniczna")
    signal = "Neutral"
    strength = 5
    rsi = df['RSI'].iloc[-1] if not df['RSI'].isna().all() else None
    
    if rsi is not None:
        if rsi < 30:
            signal = "Kupuj"
            strength = 8
        elif rsi > 70:
            signal = "Sprzedaj"
            strength = 8
    
    st.info(f"**Sygnał:** {signal} | **Siła:** {strength}/10 | **RSI:** {rsi:.2f}" if rsi is not None else "Brak danych RSI")
    
    # Volatility
    df['returns'] = df[close_col].pct_change()
    volatility = df['returns'].rolling(30).std().iloc[-1]*100 if not df['returns'].isna().all() else None
    st.write(f"📊 **Volatility (30 dni):** {volatility:.2f}%" if volatility is not None else "Brak danych dla zmienności")
