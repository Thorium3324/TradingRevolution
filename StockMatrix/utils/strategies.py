import pandas as pd
import plotly.graph_objects as go

def sma_crossover_strategy(df, short_window=20, long_window=50):
    df['SMA_short'] = df['Close'].rolling(short_window).mean()
    df['SMA_long'] = df['Close'].rolling(long_window).mean()
    df['Signal'] = 0
    df.loc[df['SMA_short'] > df['SMA_long'], 'Signal'] = 1
    df.loc[df['SMA_short'] < df['SMA_long'], 'Signal'] = -1
    df['Equity'] = (df['Signal'].shift(1) * df['Close'].pct_change()).cumsum()
    return df

def multi_strategy_backtest(df, strategies):
    fig = go.Figure()
    for strat_name, strat_func in strategies.items():
        df_temp = strat_func(df.copy())
        fig.add_trace(go.Scatter3d(
            x=df_temp.index, y=[strat_name]*len(df_temp), z=df_temp['Equity'],
            mode='lines', name=strat_name
        ))
    fig.update_layout(title="3D Equity Curve - Multi Strategy", scene=dict(
        xaxis_title="Data", yaxis_title="Strategia", zaxis_title="Kapitał"
    ))
    return fig
