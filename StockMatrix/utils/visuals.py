import plotly.graph_objects as go
import streamlit as st

def plot_candlestick_chart(df, symbol):
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Świece"
        )
    ])
    fig.update_layout(title=f"📊 Wykres świecowy {symbol}", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

def plot_volume_chart(df, symbol):
    fig = go.Figure(data=[
        go.Bar(x=df.index, y=df["Volume"], name="Wolumen", marker_color="lightblue")
    ])
    fig.update_layout(title=f"🔹 Wolumen {symbol}", template="plotly_dark", height=300)
    st.plotly_chart(fig, use_container_width=True)
