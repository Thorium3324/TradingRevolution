from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

def add_technical_indicators(df, close_col):
    close_data = df[close_col]
    df['SMA'] = SMAIndicator(close_data, 20).sma_indicator()
    df['EMA'] = EMAIndicator(close_data, 20).ema_indicator()
    df['RSI'] = RSIIndicator(close_data, 14).rsi()
    macd = MACD(close_data)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close_data)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['ATR'] = AverageTrueRange(df['High'], df['Low'], close_data, 14).average_true_range()
    df['Stochastic'] = StochasticOscillator(df['High'], df['Low'], close_data, 14).stoch()
    df['ADX'] = ADXIndicator(df['High'], df['Low'], close_data, 14).adx()
    return df
