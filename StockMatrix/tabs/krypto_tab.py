import streamlit as st
from utils.data_fetch import get_crypto_data, find_price_columns
import plotly.graph_objects as go

def krypto_tab():
    st.title("💎 Analiza kryptowalut")
    ticker = st.text_input("Symbol kryptowaluty (np. BTC, ETH):", "BTC")
    df = get_crypto_data(ticker)

    if df.empty:
        st.error("❌ Nie udało się pobrać danych.")
        return

    close_col = find_price_columns(df)
    if not close_col:
        st.error("❌ Brak kolumny zamknięcia w danych.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[close_col], name=ticker))
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)
