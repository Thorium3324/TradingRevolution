import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator

st.set_page_config(layout="wide", page_title="Trading Revolution - Akcje")

st.title("Trading Revolution - Zakładka Akcje")

# --- Wybór tickera ---
ticker = st.text_input("Wprowadź symbol akcji:", value="AAPL").upper()

if not ticker:
    st.warning("Proszę wpisać symbol akcji.")
    st.stop()

# --- Pobranie danych ---
try:
    df = yf.download(ticker, period="6mo", interval="1d")
    if df.empty:
        st.warning(f"Nie znaleziono danych dla {ticker}. Spróbuj inny symbol.")
        st.stop()
except Exception as e:
    st.error(f"Błąd pobierania danych: {e}")
    st.stop()

# --- Ujednolicenie kolumn w razie MultiIndex ---
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [' '.join(filter(None, col)).strip() for col in df.columns]

# --- Wykrywanie kolumn ---
def find_column(df, keywords):
    for col in df.columns:
        if any(k.lower() in col.lower() for k in keywords):
            return col
    return None

cols = {
    'Open': find_column(df, ['Open']),
    'High': find_column(df, ['High']),
    'Low': find_column(df, ['Low']),
    'Close': find_column(df, ['Close', 'Adj Close']),
    'Volume': find_column(df, ['Volume'])
}

missing = [k for k, v in cols.items() if v is None]
if missing:
    st.warning(f"Brakuje kolumny/kolumn: {missing}. Niektóre funkcje mogą nie działać.")

# --- Konwersja kolumn na liczby ---
for k, col_name in cols.items():
    if col_name and isinstance(df[col_name], (pd.Series, pd.DataFrame)):
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')

# --- Drop NaN w wymaganych kolumnach ---
existing_cols = [v for v in cols.values() if v]
df = df.dropna(subset=existing_cols)

# --- Wyświetlenie podstawowych metryk ---
if cols['Close']:
    last_close = df[cols['Close']].iloc[-1]
    st.metric("Cena (USD)", f"${last_close:.2f}")

# --- Dodanie wskaźników technicznych ---
def add_indicators(df, close_col):
    if close_col is None:
        return df
    df['SMA20'] = SMAIndicator(df[close_col], 20).sma_indicator()
    df['EMA20'] = EMAIndicator(df[close_col], 20).ema_indicator()
    df['RSI14'] = RSIIndicator(df[close_col], 14).rsi()
    macd = MACD(df[close_col])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    return df

df = add_indicators(df, cols['Close'])

# --- Wykres świecowy ---
if all([cols[k] for k in ['Open','High','Low','Close']]):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df[cols['Open']],
        high=df[cols['High']],
        low=df[cols['Low']],
        close=df[cols['Close']],
        name=ticker
    )])
    # Dodanie SMA i EMA do wykresu
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='blue', width=1), name='SMA20'))
    if 'EMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='orange', width=1), name='EMA20'))

    fig.update_layout(title=f"Wykres świecowy {ticker}",
                      xaxis_title="Data",
                      yaxis_title="Cena (USD)",
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Brakuje wymaganych kolumn do wykresu świecowego: Open/High/Low/Close")

# --- Wolumen ---
if cols['Volume']:
    fig_vol = go.Figure(data=[go.Bar(x=df.index, y=df[cols['Volume']], name="Wolumen")])
    fig_vol.update_layout(title=f"Wolumen {ticker}", xaxis_title="Data", yaxis_title="Wolumen")
    st.plotly_chart(fig_vol, use_container_width=True)

# --- RSI / MACD ---
if 'RSI14' in df.columns and 'MACD' in df.columns:
    st.subheader("Wskaźniki techniczne")
    col1, col2 = st.columns(2)
    col1.metric("RSI (14)", f"{df['RSI14'].iloc[-1]:.2f}")
    col2.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")

st.success("Dane i wskaźniki wczytane poprawnie!")
