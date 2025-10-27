import streamlit as st
from utils.data_fetch import get_stock_data, find_price_columns
from utils.indicators import compute_indicators
from utils.visuals import plot_candlestick_chart, plot_volume_chart
from utils.ml_predict import predict_trend
from utils.risk_metrics import analyze_volatility

def akcje_tab():
    st.title("📈 TradingRevolution — Akcje")
    symbol = st.text_input("Ticker (np. AAPL):", "AAPL").upper()
    period = st.selectbox("Okres danych:", ["1mo","3mo","6mo","1y","5y","max"], index=3)

    if st.button("Pobierz dane"):
        df = get_stock_data(symbol, period)
        if df is None or df.empty:
            st.error("Nie udało się pobrać danych. Sprawdź symbol.")
            return

        # znajdź kolumny
        open_col, high_col, low_col, close_col, vol_col = find_price_columns(df)
        if not all([open_col, high_col, low_col, close_col]):
            st.error("Brakuje kolumn Open/High/Low/Close w pobranych danych.")
            return

        # compute indicators (adds columns to df)
        df = compute_indicators(df, close_col, high_col=high_col, low_col=low_col)

        # top row: candlestick & metrics
        col1, col2 = st.columns([3,1])
        with col1:
            plot_candlestick_chart(df, symbol, open_col, high_col, low_col, close_col)
        with col2:
            # Technical Analysis Panel
            price = df[close_col].iloc[-1]
            change_24h = ((df[close_col].iloc[-1] - df[close_col].iloc[-2]) / df[close_col].iloc[-2])*100 if len(df) > 1 else 0
            rsi = df["RSI"].iloc[-1] if "RSI" in df.columns else None
            macd = df["MACD"].iloc[-1] if "MACD" in df.columns else None
            vol30 = df[close_col].pct_change().dropna()[-30:].std()*100 if len(df) >= 30 else 0
            st.metric("Price (USD)", f"${price:.2f}", f"{change_24h:.2f}%")
            st.metric("RSI (14)", f"{rsi:.2f}" if rsi is not None else "n/a")
            st.metric("MACD", f"{macd:.4f}" if macd is not None else "n/a")
            st.metric("Volatility (30d)", f"{vol30:.2f}%")
            pred, signal = predict_trend(df, close_col)
            st.markdown(f"**Signal:** {signal} — {pred}")

            if vol30 > 10:
                st.warning("High volatility detected – expect larger price swings ⚠️")

        # volume chart
        if vol_col:
            plot_volume_chart(df, symbol, vol_col)

        # lower panels: indicators table + ml + risk
        st.subheader("Indicators (last 20 rows)")
        st.dataframe(df.tail(20))

        with st.expander("AI / ML prediction details"):
            pred, signal = predict_trend(df, close_col)
            st.write("Prediction:", pred)
            st.write("Signal:", signal)

        with st.expander("Risk Metrics"):
            report = analyze_volatility(df, close_col)
            for k,v in report.items():
                st.write(f"**{k}:** {v}")
