# app.py - pełny działający plik Streamlit z zakładkami Akcje i Krypto

import streamlit as st
from tabs.akcje_tab import akcje_tab
from tabs.krypto_tab import krypto_tab

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide")

st.title("TradingRevolution Ultimate")

tabs = st.tabs(["Akcje", "Krypto"])

with tabs[0]:
    akcje_tab()

with tabs[1]:
    krypto_tab()
