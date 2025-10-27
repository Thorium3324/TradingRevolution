import numpy as np

def analyze_volatility(df):
    df["returns"] = df["Close"].pct_change()
    volatility = np.std(df["returns"].dropna()) * np.sqrt(252)
    sharpe = (df["returns"].mean() / df["returns"].std()) * np.sqrt(252)

    return {
        "Volatility (annualized)": f"{volatility:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Signal Strength": "⚠️ High Volatility" if volatility > 0.3 else "✅ Stable"
    }

def portfolio_summary(df):
    if "Returns" not in df.columns:
        df["Returns"] = df["Close"].pct_change()
    total_return = (1 + df["Returns"]).prod() - 1
    return {"Total Return": f"{total_return:.2%}", "Mean Return": f"{df['Returns'].mean():.2%}"}
