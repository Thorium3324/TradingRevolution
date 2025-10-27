import streamlit as st
from tabs.akcje_tab import akcje_tab
# Inne zakładki, możesz je stworzyć analogicznie w folderze tabs
# from tabs.krypto_tab import krypto_tab
# from tabs.ai_tab import ai_tab
# from tabs.alerty_tab import alerty_tab
# from tabs.analityka_tab import analityka_tab
# from tabs.strategie_tab import strategie_tab

st.set_page_config(page_title="TradingRevolution Ultimate", layout="wide")

# --- Panel zakładek ---
tabs = ["Akcje", "AI", "Alerty", "Analityka", "Strategie"]
selected_tab = st.sidebar.radio("Wybierz zakładkę:", tabs)

if selected_tab == "Akcje":
    akcje_tab()
# elif selected_tab == "Krypto":
#     krypto_tab()
# elif selected_tab == "AI":
#     ai_tab()
# elif selected_tab == "Alerty":
#     alerty_tab()
# elif selected_tab == "Analityka":
#     analityka_tab()
# elif selected_tab == "Strategie":
#     strategie_tab()
