import streamlit as st
from tabs.akcje_tab import akcje_tab
from tabs.krypto_tab import krypto_tab
from tabs.portfolio_tab import portfolio_tab
from tabs.strategie_tab import strategie_tab
from tabs.alerty_tab import alerty_tab

st.set_page_config(page_title="TradingRevolution", layout="wide", page_icon="💹")

# Load CSS
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Sidebar & nav
st.sidebar.image("assets/logo.png", use_column_width=True) if st.sidebar else None
st.sidebar.title("TradingRevolution")
tab = st.sidebar.radio("Nawigacja", ["Akcje", "Krypto", "Strategie", "Portfolio", "Alerty"])

if tab == "Akcje":
    akcje_tab()
elif tab == "Krypto":
    krypto_tab()
elif tab == "Strategie":
    strategie_tab()
elif tab == "Portfolio":
    portfolio_tab()
elif tab == "Alerty":
    alerty_tab()
else:
    st.info("Zakładka w budowie")
