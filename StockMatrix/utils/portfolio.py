import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def parse_holdings(text):
    holdings = {}
    for item in text.split(","):
        try:
            ticker, qty = item.split(":")
            holdings[ticker.strip().upper()] = float(qty)
        except: continue
    return holdings

def calculate_portfolio(holdings):
    tickers = list(holdings.keys())
    data = yf.download(tickers, period="1d")['Close'].iloc[-1]
    df = pd.DataFrame(columns=['Quantity','Price','Value'])
    total = 0
    for t, q in holdings.items():
        price = data[t]
        df.loc[t] = [q, price, q*price]
        total += q*price
    return df, total

def plot_portfolio_pie(df):
    fig = px.pie(df, names=df.index, values='Value', title="Portfolio allocation")
    return fig

def plot_portfolio_3d(df):
    fig = go.Figure(data=[go.Bar3d(
        x=df.index, y=df['Quantity'], z=df['Value'],
        dx=0.5, dy=0.5, dz=df['Value'], color=df['Value'], colorscale='Viridis'
    )])
    fig.update_layout(title="3D Portfolio Overview", scene=dict(
        xaxis_title='Ticker', yaxis_title='Quantity', zaxis_title='Value'
    ))
    return fig
