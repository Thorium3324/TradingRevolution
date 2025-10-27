import streamlit as st
import sys, os

# --- ŚCIEŻKI ---
sys.path.append(os.path.join(os.path.dirname(__file__), 'tabs'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# --- IMPORTY ZAKŁADEK ---
from tabs.akcje_tab import akcje_tab
from tabs.krypto_tab import krypto_tab
from tabs.portfolio_tab import portfolio_tab
from tabs.strategie_tab import strategie_tab
from tabs.alerty_tab import alerty_tab
from tabs.analityka_tab import analityka_tab
from tabs.ai_tab import ai_tab

# --- USTAWIENIA STRONY ---
st.set_page_config(page_title="TradingRevolution", layout="wide")
st.title("🚀 TradingRevolution — Ultimate Trading Dashboard")

# --- MENU ---
tabs = st.sidebar.radio(
    "📊 Wybierz sekcję:",
    ["Akcje", "Krypto", "Portfolio", "Strategie", "Alerty", "Analityka", "AI"]
)

# --- ROUTING ---
if tabs == "Akcje":
    akcje_tab()
elif tabs == "Krypto":
    krypto_tab()
elif tabs == "Portfolio":
    portfolio_tab()
elif tabs == "Strategie":
    strategie_tab()
elif tabs == "Alerty":
    alerty_tab()
elif tabs == "Analityka":
    analityka_tab()
elif tabs == "AI":
    ai_tab()
