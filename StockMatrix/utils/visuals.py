import plotly.graph_objects as go
import pandas as pd

def advanced_candlestick_chart(df, title="Wykres świecowy", indicators=["SMA20","EMA20","RSI"]):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Candlestick"
    ))
    if "SMA20" in indicators and "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA20", line=dict(color="orange")))
    if "EMA20" in indicators and "EMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="green")))
    if "RSI" in indicators and "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="blue"), yaxis="y2"))
        fig.update_layout(yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0,100]))
    fig.update_layout(title=title, template="plotly_dark")
    return fig