import streamlit as st
from tabs.akcje_tab import akcje_tab

st.set_page_config(page_title="TradingRevolution", layout="wide")
st.title("TradingRevolution - Ultimate Stock & Crypto Dashboard")

# --- Sidebar ---
tab = st.sidebar.selectbox("Wybierz zakładkę:", ["Akcje"])

if tab == "Akcje":
    akcje_tab()
