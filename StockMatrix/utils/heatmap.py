import plotly.graph_objects as go

def plot_prediction_heatmap(df_actual, df_pred):
    df_pct = ((df_pred - df_actual)/df_actual).T * 100
    fig = go.Figure()
    for col in df_pct.columns:
        fig.add_trace(go.Heatmap(z=df_pct[col].values.reshape(1,-1), x=df_pct.index, y=[col]*len(df_pct.index),
                                 colorscale='RdYlGn', showscale=True))
    fig.update_layout(title="Heatmapa Predykcyjna", template="plotly_dark")
    return fig
