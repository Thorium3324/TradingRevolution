import numpy as np
from sklearn.linear_model import LinearRegression

def predict_trend(df):
    if "Close" not in df.columns:
        return "brak danych", "Neutral"

    y = df["Close"].values
    X = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    trend = model.predict([[len(y)+1]])[0]

    if trend > y[-1]:
        return "Wzrost", "Kupno"
    elif trend < y[-1]:
        return "Spadek", "Sprzedaż"
    else:
        return "Neutralny", "Trzymaj"
