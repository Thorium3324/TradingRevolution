import streamlit as st
from utils.data_fetch import get_crypto_data, find_price_columns
from utils.indicators import compute_indicators
from utils.visuals import plot_candlestick_chart, plot_volume_chart
from utils.ml_predict import predict_trend

def krypto_tab():
    st.title("💹 TradingRevolution — Krypto")
    symbol = st.text_input("Ticker (np. BTC-USD):", "BTC-USD").upper()
    period = st.selectbox("Okres danych:", ["1mo","3mo","6mo","1y","5y","max"], index=0)
    interval = st.selectbox("Interwał:", ["1d","1h","4h"], index=0)

    if st.button("Pobierz dane Krypto"):
        df = get_crypto_data(symbol, period, interval)
        if df is None or df.empty:
            st.error("Nie udało się pobrać danych.")
            return

        open_col, high_col, low_col, close_col, vol_col = find_price_columns(df)
        if not all([open_col, high_col, low_col, close_col]):
            st.error("Brakuje wymaganych kolumn w danych.")
            return

        df = compute_indicators(df, close_col, high_col=high_col, low_col=low_col)

        plot_candlestick_chart(df, symbol, open_col, high_col, low_col, close_col)
        if vol_col:
            plot_volume_chart(df, symbol, vol_col)

        st.subheader("Technical Analysis")
        price = df[close_col].iloc[-1]
        change_24h = ((df[close_col].iloc[-1] - df[close_col].iloc[-2]) / df[close_col].iloc[-2]) * 100 if len(df) > 1 else 0
        st.metric("Price (USD)", f"${price:.2f}", f"{change_24h:.2f}%")
        pred, signal = predict_trend(df, close_col)
        st.write("ML Signal:", signal)
