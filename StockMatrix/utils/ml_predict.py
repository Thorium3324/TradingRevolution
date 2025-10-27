import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
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

@st.cache_data(ttl=3600)
def predict_next_day_lstm(df, n_steps=20):
    df = df[['Close']].copy()
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df)
    X, y = [], []
    for i in range(n_steps, len(df_scaled)):
        X.append(df_scaled[i-n_steps:i,0])
        y.append(df_scaled[i,0])
    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)
    last_seq = df_scaled[-n_steps:].reshape(1,n_steps,1)
    pred_scaled = model.predict(last_seq, verbose=0)[0,0]
    return scaler.inverse_transform([[pred_scaled]])[0,0]

def predict_trend(df):
    xgb_pred = predict_next_day_xgb(df)
    lstm_pred = predict_next_day_lstm(df)
    last_price = df['Close'].iloc[-1]
    trend_xgb = "Bullish" if xgb_pred > last_price else "Bearish"
    trend_lstm = "Bullish" if lstm_pred > last_price else "Bearish"
    avg_pred = (xgb_pred + lstm_pred)/2
    trend = "Bullish" if avg_pred > last_price else "Bearish"
    return avg_pred, trend, trend_xgb, trend_lstm
