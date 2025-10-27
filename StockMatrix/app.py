import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import date

st.set_page_config(page_title="TradingRevolution Ultra EVO 5.3", layout="wide", page_icon="💹")
st.sidebar.title("TradingRevolution Ultra EVO 5.3")
tabs = st.sidebar.radio("Sekcje:", ["Akcje","Krypto","Portfolio","Backtesting","AI Predykcje","Heatmapa","Alerty","Live Trading"])

# --- ZAKŁADKA AKCJE ---
if tabs == "Akcje":
    st.title("Zakładka Akcje - TradingRevolution")
    ticker = st.text_input("Ticker:", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())
    
    if ticker:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            st.warning(f"Brak danych dla {ticker}")
        else:
            # --- Przygotowanie danych ---
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            
            for col in ['Open','High','Low','Close','Adj Close','Volume']:
                if col in df.columns:
                    # jeśli kolumna jest DataFrame lub MultiIndex, bierzemy pierwszą kolumnę
                    if isinstance(df[col], pd.DataFrame):
                        df[col] = df[col].iloc[:,0]
                    # jeśli typ nie jest Series, wymuszamy Series
                    if not isinstance(df[col], pd.Series):
                        df[col] = pd.Series(df[col])
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['Open','High','Low','Close'])
            
            # --- Wskaźniki ---
            close = df['Close']
            df['SMA20'] = SMAIndicator(close, 20).sma_indicator()
            df['EMA20'] = EMAIndicator(close, 20).ema_indicator()
            df['RSI'] = RSIIndicator(close, 14).rsi()
            macd = MACD(close)
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            bb = BollingerBands(close)
            df['BB_upper'] = bb.bollinger_hband()
            df['BB_lower'] = bb.bollinger_lband()
            
            # --- Sygnały buy/sell ---
            df['Signal'] = ""
            df.loc[(df['Close'] > df['SMA20']) & (df['RSI'] < 70), 'Signal'] = "BUY"
            df.loc[(df['Close'] < df['SMA20']) & (df['RSI'] > 30), 'Signal'] = "SELL"
            
            # --- Wykres świecowy ---
            fig_candle = go.Figure()
            fig_candle.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Świece"
            ))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="SMA20"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='green', width=2), name="EMA20"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB_upper"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB_lower"))
            fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
            
            # --- RSI ---
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name="RSI"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="RSI (14)", template="plotly_dark", height=250)
            
            # --- MACD ---
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='cyan', width=2), name="MACD"))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], line=dict(color='yellow', width=2), name="MACD Signal"))
            fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)
            
            # --- Wolumen ---
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Wolumen", marker_color='blue'))
            fig_vol.update_layout(title="Wolumen", template="plotly_dark", height=200)
            
            # --- Wyświetlenie ---
            st.plotly_chart(fig_candle, use_container_width=True)
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.plotly_chart(fig_macd, use_container_width=True)
            st.plotly_chart(fig_vol, use_container_width=True)
            
            st.subheader("Ostatnie sygnały Buy/Sell")
            st.dataframe(df[['Close','SMA20','RSI','Signal']].tail(20))
