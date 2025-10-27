import yfinance as yf

def check_alerts(symbol):
    df = yf.download(symbol, period="1mo")
    alerts = []
    if df["Close"].iloc[-1] > df["Close"].mean():
        alerts.append(f"{symbol}: Cena powyżej średniej – możliwy trend wzrostowy.")
    if df["Close"].iloc[-1] < df["Close"].mean():
        alerts.append(f"{symbol}: Cena poniżej średniej – możliwy trend spadkowy.")
    if len(alerts) == 0:
        alerts.append("Brak alertów – rynek stabilny.")
    return alerts
