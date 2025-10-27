import streamlit as st
import pandas as pd
from utils.risk_metrics import portfolio_summary

def portfolio_tab():
    st.title("📁 Portfolio")
    st.markdown("Wgraj CSV z kolumnami: symbol, quantity, price (opcjonalnie close)")
    uploaded = st.file_uploader("Wgraj CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df)
        summary = portfolio_summary(df)
        st.json(summary)
