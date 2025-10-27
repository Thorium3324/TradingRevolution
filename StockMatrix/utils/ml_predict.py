import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import streamlit as st

@st.cache_data(ttl=3600)
def predict_next_day(df, model_type='xgboost'):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df.dropna(inplace=True)
    X = pd.DataFrame({'Open': df['Open'], 'High': df['High'], 'Low': df['Low'], 'Volume': df['Volume']})
    y = df['Close'].shift(-1)[:-1]
    X = X[:-1]
    if model_type=='xgboost':
        model = XGBRegressor(n_estimators=200, learning_rate=0.1)
    else:
        model = RandomForestRegressor(n_estimators=200)
    model.fit(X, y)
    next_day = X.iloc[-1].values.reshape(1, -1)
    pred = model.predict(next_day)[0]
    return pred

def predict_trend_and_volume(df):
    df['Return'] = df['Close'].pct_change()
    X = df[['Open','High','Low','Close','Volume']].shift(1).dropna()
    y_price = df['Close'][1:]
    y_vol = df['Volume'][1:]
    
    model_price = XGBRegressor(n_estimators=200)
    model_vol = XGBRegressor(n_estimators=100)
    model_price.fit(X, y_price)
    model_vol.fit(X, y_vol)
    
    next_input = X.iloc[-1].values.reshape(1,-1)
    next_price = model_price.predict(next_input)[0]
    next_vol = model_vol.predict(next_input)[0]
    
    trend = "Bullish" if next_price > df['Close'].iloc[-1] else "Bearish"
    return next_price, next_vol, trend