import numpy as np
from sklearn.linear_model import LinearRegression

def predict_trend(df, close_col):
    """
    Lightweight trend predictor using linear regression on index -> price.
    Returns (predicted_price, signal_label)
    """
    try:
        data = df[close_col].dropna().values
        if len(data) < 10:
            return (None, "Not enough data")
        X = np.arange(len(data)).reshape(-1,1)
        y = data
        model = LinearRegression().fit(X, y)
        next_pred = model.predict([[len(data)]])[0]
        last = data[-1]
        if next_pred > last * 1.001:    # small threshold
            return (round(next_pred,4), "BUY")
        elif next_pred < last * 0.999:
            return (round(next_pred,4), "SELL")
        else:
            return (round(next_pred,4), "HOLD")
    except Exception as e:
        return (None, "Error")
