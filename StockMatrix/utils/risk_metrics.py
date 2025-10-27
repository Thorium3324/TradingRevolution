import numpy as np

def analyze_volatility(df, close_col):
    res = {}
    returns = df[close_col].pct_change().dropna()
    if returns.empty:
        return {"error":"not enough data"}
    vol_30d = returns[-30:].std() * 100
    annual_vol = returns.std() * np.sqrt(252) * 100
    sharpe = (returns.mean()/returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
    res["Volatility 30d (%)"] = f"{vol_30d:.2f}%"
    res["Annualized Volatility (%)"] = f"{annual_vol:.2f}%"
    res["Sharpe Ratio"] = f"{sharpe:.2f}"
    res["Volatility Flag"] = "High" if vol_30d > 10 else "Normal"
    return res

def portfolio_summary(df):
    # expects columns: symbol, quantity, price (or Close)
    df = df.copy()
    if "price" in df.columns:
        df["market_value"] = df["quantity"] * df["price"]
    elif "Close" in df.columns and "quantity" in df.columns:
        df["market_value"] = df["quantity"] * df["Close"]
    else:
        return {"error":"insufficient columns"}
    total = df["market_value"].sum()
    return {"Total Market Value": total, "Holdings Count": len(df)}
