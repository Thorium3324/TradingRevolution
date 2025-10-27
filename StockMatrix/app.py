import streamlit as st
from tabs.akcje_tab import akcje_tab
from tabs.krypto_tab import krypto_tab

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide")

st.title("TradingRevolution Ultimate Dashboard")

# --- Panel zakładek ---
tab = st.tabs(["Akcje", "Krypto"])

with tab[0]:
    akcje_tab()

with tab[1]:
    krypto_tab()
