import pandas as pd
import numpy as np

def sharpe_ratio(returns, risk_free=0.01):
    return (returns.mean() - risk_free/252) / returns.std() * np.sqrt(252)

def max_drawdown(equity_curve):
    roll_max = equity_curve.cummax()
    drawdown = equity_curve/roll_max - 1
    return drawdown.min()

def volatility(returns):
    return returns.std() * np.sqrt(252)

def beta(returns, benchmark_returns):
    cov = np.cov(returns, benchmark_returns)[0,1]
    var = np.var(benchmark_returns)
    return cov / var

def alpha(returns, benchmark_returns, risk_free=0.01):
    b = beta(returns, benchmark_returns)
    return returns.mean() - (risk_free/252 + b*(benchmark_returns.mean() - risk_free/252))
