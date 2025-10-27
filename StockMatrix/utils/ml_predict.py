import pandas as pd
from xgboost import XGBRegressor
import streamlit as st

@st.cache_data(ttl=3600)
def predict_next_day_xgb(df):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df.dropna(inplace=True)
    X = df[['Open','High','Low','Volume']]
    y = df['Close'].shift(-1)[:-1]
    X = X[:-1]
    model = XGBRegressor(n_estimators=300)
    model.fit(X, y)
    next_input = X.iloc[-1].values.reshape(1, -1)
    return model.predict(next_input)[0]

def predict_trend(df):
    next_price = predict_next_day_xgb(df)
    last_price = df['Close'].iloc[-1]
    trend = "Bullish" if next_price > last_price else "Bearish"
    return next_price, trend
