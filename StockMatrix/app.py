import streamlit as st
from tabs.akcje import akcje_tab
from tabs.krypto import krypto_tab
from tabs.portfolio import portfolio_tab
from tabs.ml_predict import ml_tab
from tabs.heatmapa import heatmap_tab
from tabs.strategies import strategies_tab
from tabs.alerts import alerts_tab

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide", page_icon="💹")
st.sidebar.title("TradingRevolution Ultimate")

tab = st.sidebar.radio("Wybierz zakładkę:", [
    "Akcje","Krypto","Portfolio","AI Predykcje","Heatmapa","Strategie","Alerty"
])

if tab == "Akcje":
    akcje_tab()
elif tab == "Krypto":
    krypto_tab()
elif tab == "Portfolio":
    portfolio_tab()
elif tab == "AI Predykcje":
    ml_tab()
elif tab == "Heatmapa":
    heatmap_tab()
elif tab == "Strategie":
    strategies_tab()
elif tab == "Alerty":
    alerts_tab()
else:
    st.info("Zakładka w budowie")
