import plotly.figure_factory as ff
import numpy as np
import streamlit as st

def show_correlation_heatmap(df):
    corr = df.corr()
    z = np.array(corr)
    fig = ff.create_annotated_heatmap(
        z, x=list(corr.columns), y=list(corr.columns),
        colorscale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
