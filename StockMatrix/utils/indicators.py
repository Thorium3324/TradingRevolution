import ta
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def compute_indicators(df, close_col, high_col=None, low_col=None, sma_window=20, ema_window=50):
    # ensure col names exist
    close = df[close_col]
    # SMA, EMA
    df['SMA'] = SMAIndicator(close, sma_window).sma_indicator()
    df['EMA'] = EMAIndicator(close, ema_window).ema_indicator()
    # RSI
    df['RSI'] = RSIIndicator(close, 14).rsi()
    # MACD
    macd = MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    # Bollinger
    bb = BollingerBands(close)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    # ATR, Stochastic, ADX if possible
    if high_col and low_col:
        high = df[high_col]
        low = df[low_col]
        df['ATR'] = AverageTrueRange(high, low, close, 14).average_true_range()
        df['Stochastic'] = StochasticOscillator(high, low, close, 14).stoch()
        df['ADX'] = ADXIndicator(high, low, close, 14).adx()
    return df
