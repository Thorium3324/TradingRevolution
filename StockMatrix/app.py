import streamlit as st
from datetime import date
from utils.data_fetch import get_stock_data, get_crypto_data
from utils.indicators import add_technical_indicators
from utils.strategies import sma_crossover_strategy, multi_strategy_backtest
from utils.portfolio import parse_holdings, calculate_portfolio, plot_portfolio_pie, plot_portfolio_3d
from utils.ml_predict import predict_next_day, predict_trend
from utils.alerts import set_alert, check_alert
from utils.heatmap import plot_prediction_heatmap
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="TradingRevolution Ultra EVO 5.2", layout="wide", page_icon="💹")
st.markdown('<link rel="stylesheet" href="styles.css">', unsafe_allow_html=True)

st.sidebar.title("TradingRevolution Ultra EVO 5.2")
tabs = st.sidebar.radio("Sekcje:", ["Akcje","Krypto","Portfolio","Backtesting","AI Predykcje","Heatmapa","Alerty","Live Trading"])

# --- AKCJE ---
if tabs=="Akcje":
    ticker = st.text_input("Ticker:", "AAPL").upper()
    start_date = st.date_input("Start:", date(2023,1,1))
    end_date = st.date_input("End:", date.today())
    if ticker:
        df = get_stock_data(ticker, start_date, end_date)
        df = add_technical_indicators(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Close", line=dict(color="#ff7f50")))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA20", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="green")))
        st.plotly_chart(fig, use_container_width=True)

# --- Krypto ---
elif tabs=="Krypto":
    exchange = st.selectbox("Exchange", ["binance","coinbasepro"])
    symbol = st.text_input("Symbol:", "BTC/USDT")
    df = get_crypto_data(exchange, symbol)
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
    df = sma_crossover_strategy(df)
    st.line_chart(df['Equity'])

# --- AI PREDYKCJE ---
elif tabs=="AI Predykcje":
    ticker = st.text_input("Ticker do predykcji:", "AAPL", key="ai")
    df = get_stock_data(ticker, date(2023,1,1), date.today())
    next_price, trend = predict_trend(df)
    st.metric(f"Predykcja następnej ceny {ticker}", f"${next_price:.2f}")
    st.info(f"Trend: {trend}")

# --- HEATMAPA ---
elif tabs=="Heatmapa":
    st.info("Heatmapa predykcyjna dostępna w kolejnej wersji AI/ML Ultra EVO")

# --- ALERTY ---
elif tabs=="Alerty":
    ticker = st.text_input("Ticker do alertu:", "AAPL", key="alert")
    price = st.number_input("Cena alertu:", 0.0)
    if st.button("Ustaw alert"):
        set_alert(ticker, price)

# --- LIVE TRADING ---
elif tabs=="Live Trading":
    st.warning("Live trading dostępny po konfiguracji API w broker_integration.py")
