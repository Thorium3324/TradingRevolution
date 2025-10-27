from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import pandas as pd

def add_technical_indicators(df):
    df = df.copy()
    
    # --- zabezpieczenie Close ---
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:,0]
    else:
        close = df['Close']
    
    # upewniamy się, że float i brak NaN
    close = pd.to_numeric(close, errors='coerce')
    close = close.fillna(method='ffill').fillna(method='bfill')

    # --- wskaźniki ---
    df['SMA20'] = SMAIndicator(close, 20).sma_indicator()
    df['EMA20'] = EMAIndicator(close, 20).ema_indicator()
    df['RSI'] = RSIIndicator(close, 14).rsi()
    macd = MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    
    return df
