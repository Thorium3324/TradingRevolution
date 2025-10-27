import pandas as pd
import ta

def compute_indicators(df):
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["MACD"] = ta.trend.MACD(df["Close"]).macd()
    df["SMA20"] = ta.trend.SMAIndicator(df["Close"], 20).sma_indicator()
    df["EMA50"] = ta.trend.EMAIndicator(df["Close"], 50).ema_indicator()
    return df
