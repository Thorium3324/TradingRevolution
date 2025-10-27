import streamlit as st
from datetime import date
from utils.data_fetch import get_stock_data, get_crypto_data
from utils.indicators import add_technical_indicators
from utils.strategies import sma_crossover_strategy, multi_strategy_backtest
from utils.portfolio import parse_holdings, calculate_portfolio, plot_portfolio_pie, plot_portfolio_3d
from utils.ml_predict import predict_trend
from utils.alerts import set_alert, check_alerts
from utils.heatmap import plot_prediction_heatmap
from utils.broker_integration import fetch_live_price, place_order
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# --- konfiguracja strony ---
st.set_page_config(page_title="TradingRevolution Ultra EVO 5.3", layout="wide", page_icon="💹")
st.markdown('<link rel="stylesheet" href="styles.css">', unsafe_allow_html=True)
st.sidebar.title("TradingRevolution Ultra EVO 5.3")

# --- zakładki ---
tabs = st.sidebar.radio("Sekcje:", ["Akcje","Krypto","Portfolio","Backtesting","AI Predykcje","Heatmapa","Alerty","Live Trading"])

# --- AKCJE ---
if tabs=="Akcje":
    ticker = st.text_input("Ticker:", "AAPL").upper()
    start_date = st.date_input("Start:", date(2023,1,1))
    end_date = st.date_input("End:", date.today())
    
    if ticker:
        df = get_stock_data(ticker, start_date, end_date)
        if df is None or df.empty:
            st.warning(f"Brak danych dla {ticker}")
        else:
            df = add_technical_indicators(df)
            
            # --- Wykres świecowy z SMA/EMA ---
            fig_candle = go.Figure()
            fig_candle.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Świece"
            ))
            fig_candle.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA20'],
                line=dict(color='orange', width=2),
                name="SMA20"
            ))
            fig_candle.add_trace(go.Scatter(
                x=df.index,
                y=df['EMA20'],
                line=dict(color='green', width=2),
                name="EMA20"
            ))
            fig_candle.update_layout(
                title=f"Wykres świecowy {ticker} z SMA/EMA",
                xaxis_title="Data",
                yaxis_title="Cena",
                template="plotly_dark",
                height=600
            )
            
            # --- RSI ---
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                line=dict(color='magenta', width=2),
                name="RSI"
            ))
            fig_rsi.update_layout(
                title="RSI (14)",
                xaxis_title="Data",
                yaxis_title="RSI",
                template="plotly_dark",
                height=250
            )
            
            # --- MACD ---
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD'],
                line=dict(color='cyan', width=2),
                name="MACD"
            ))
            fig_macd.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                line=dict(color='yellow', width=2),
                name="MACD Signal"
            ))
            fig_macd.update_layout(
                title="MACD",
                xaxis_title="Data",
                yaxis_title="Wartość",
                template="plotly_dark",
                height=250
            )
            
            # --- Wyświetlanie wykresów ---
            st.plotly_chart(fig_candle, use_container_width=True)
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.plotly_chart(fig_macd, use_container_width=True)

# --- Krypto ---
elif tabs=="Krypto":
    exchange = st.selectbox("Exchange", ["binance","coinbasepro"])
    symbol = st.text_input("Symbol:", "BTC/USDT")
    df = get_crypto_data(exchange, symbol)
    if df is None or df.empty:
        st.warning(f"Brak danych dla {symbol}")
    else:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
        st.plotly_chart(fig, use_container_width=True)

# --- PORTFOLIO ---
elif tabs=="Portfolio":
    portfolio_input = st.text_area("Wprowadź akcje i ilości:", "AAPL:10,TSLA:5")
    holdings = parse_holdings(portfolio_input)
    if holdings:
        df_port, total = calculate_portfolio(holdings)
        st.metric("Łączna wartość portfela", f"${total:,.2f}")
        st.dataframe(df_port)
        st.plotly_chart(plot_portfolio_pie(df_port), use_container_width=True)
        st.plotly_chart(plot_portfolio_3d(df_port), use_container_width=True)

# --- BACKTESTING ---
elif tabs=="Backtesting":
    ticker = st.text_input("Ticker strategii:", "AAPL", key="back")
    df = get_stock_data(ticker, date(2023,1,1), date.today())
    if df is None or df.empty:
        st.warning(f"Brak danych dla {ticker}")
    else:
        df = sma_crossover_strategy(df)
        st.line_chart(df['Equity'])

# --- AI PREDYKCJE ---
elif tabs=="AI Predykcje":
    ticker = st.text_input("Ticker do predykcji:", "AAPL", key="ai")
    if ticker:
        df = get_stock_data(ticker, date(2023,1,1), date.today())
        if df is None or df.empty:
            st.warning(f"Brak danych dla {ticker}")
        else:
            next_price, trend = predict_trend(df)
            st.metric(f"Predykcja następnej ceny {ticker}", f"${next_price:.2f}")
            st.info(f"Trend: {trend}")

# --- HEATMAPA ---
elif tabs=="Heatmapa":
    st.info("Heatmapa predykcyjna AI w przygotowaniu")

# --- ALERTY ---
elif tabs=="Alerty":
    ticker = st.text_input("Ticker do alertu:", "AAPL", key="alert")
    price = st.number_input("Cena alertu:", 0.0)
    if st.button("Ustaw alert"):
        set_alert(ticker, price)
    # opcjonalnie sprawdzamy alerty w czasie rzeczywistym
    current_prices = {}
    for t in [ticker]:
        try:
            df_tmp = get_stock_data(t, date.today(), date.today())
            if df_tmp is not None and not df_tmp.empty:
                current_prices[t] = df_tmp['Close'].iloc[-1]
        except:
            pass
    if current_prices:
        check_alerts(current_prices)

# --- LIVE TRADING ---
elif tabs=="Live Trading":
    st.warning("Live trading dostępny po konfiguracji API w broker_integration.py")
