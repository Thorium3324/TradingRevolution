import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide", page_icon="💹")
st.sidebar.title("TradingRevolution Ultimate")
tabs = st.sidebar.radio("Sekcje:", ["Akcje", "Krypto", "Portfolio", "Backtesting", "AI Predykcje", "Heatmapa", "Alerty", "Live Trading"])

# --- Funkcje do wykrywania formacji świecowych ---
def detect_hammer(df):
    df['Hammer'] = ((df['High'] - df['Low']) > 3*(df['Open'] - df['Close'])) & \
                   (((df['Close'] - df['Low']) / (0.001 + df['High'] - df['Low'])) > 0.6)
    return df

def detect_doji(df):
    df['Doji'] = abs(df['Close'] - df['Open']) / (df['High'] - df['Low'] + 0.001) < 0.1
    return df

def detect_engulfing(df):
    df['Engulfing'] = ((df['Close'] > df['Open']) & (df['Close'].shift(1) < df['Open'].shift(1)) & \
                       (df['Close'] > df['Open'].shift(1))) | \
                      ((df['Close'] < df['Open']) & (df['Close'].shift(1) > df['Open'].shift(1)) & \
                       (df['Close'] < df['Open'].shift(1)))
    return df

# --- ZAKŁADKA AKCJE ---
if tabs == "Akcje":
    st.title("Zakładka Akcje - TradingRevolution Ultimate")

    ticker = st.text_input("Ticker:", "AAPL").upper()
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today())

    # Slider do ustawienia okresów wskaźników
    sma_period = st.sidebar.slider("Okres SMA", 5, 100, 20)
    ema_period = st.sidebar.slider("Okres EMA", 5, 100, 20)
    rsi_period = st.sidebar.slider("Okres RSI", 5, 50, 14)

    if ticker:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            st.warning(f"Brak danych dla {ticker}")
        else:
            # --- Przygotowanie danych ---
            df = df.copy()
            df.index = pd.to_datetime(df.index)

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [' '.join(col).strip() for col in df.columns.values]

            for col in ['Open','High','Low','Close','Adj Close','Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=['Open','High','Low','Close'])

            # --- Wskaźniki ---
            close = df['Close']
            df['SMA'] = SMAIndicator(close, sma_period).sma_indicator()
            df['EMA'] = EMAIndicator(close, ema_period).ema_indicator()
            df['RSI'] = RSIIndicator(close, rsi_period).rsi()
            macd = MACD(close)
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            bb = BollingerBands(close)
            df['BB_upper'] = bb.bollinger_hband()
            df['BB_lower'] = bb.bollinger_lband()

            # --- Sygnały Buy/Sell ---
            df['Signal'] = ""
            df.loc[(df['Close'] > df['SMA']) & (df['RSI'] < 70), 'Signal'] = "BUY"
            df.loc[(df['Close'] < df['SMA']) & (df['RSI'] > 30), 'Signal'] = "SELL"

            # --- Formacje świecowe ---
            df = detect_hammer(df)
            df = detect_doji(df)
            df = detect_engulfing(df)

            # --- Wykres świecowy z kolorowymi oznaczeniami formacji ---
            fig_candle = go.Figure()
            colors = []
            for i, row in df.iterrows():
                if row['Signal'] == "BUY":
                    colors.append("green")
                elif row['Signal'] == "SELL":
                    colors.append("red")
                elif row['Hammer']:
                    colors.append("orange")
                elif row['Doji']:
                    colors.append("purple")
                elif row['Engulfing']:
                    colors.append("blue")
                else:
                    colors.append("white")

            fig_candle.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color='lime',
                decreasing_line_color='red',
                name="Świece"
            ))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=2), name=f"SMA {sma_period}"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['EMA'], line=dict(color='green', width=2), name=f"EMA {ema_period}"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='red', width=1, dash='dot'), name="BB Upper"))
            fig_candle.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='red', width=1, dash='dot'), name="BB Lower"))
            fig_candle.update_layout(title=f"{ticker} - Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)

            # --- RSI ---
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name="RSI"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title=f"RSI ({rsi_period})", template="plotly_dark", height=250)

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

            # --- Tabela sygnałów i formacji ---
            st.subheader("Ostatnie sygnały Buy/Sell i formacje świecowe")
            st.dataframe(df[['Close','SMA','EMA','RSI','Signal','Hammer','Doji','Engulfing']].tail(20))
