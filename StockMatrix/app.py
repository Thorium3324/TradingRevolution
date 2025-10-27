import streamlit as st
import os
import importlib.util

# --- Funkcja do dynamicznego importu zakładek ---
def import_tab(tab_name):
    tab_path = os.path.join(os.path.dirname(__file__), "tabs", f"{tab_name}.py")
    if not os.path.exists(tab_path):
        st.error(f"❌ Nie znaleziono zakładki: {tab_name}")
        return None
    spec = importlib.util.spec_from_file_location(tab_name, tab_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# --- Import zakładek ---
akcje_tab_module = import_tab("akcje_tab")
krypto_tab_module = import_tab("krypto_tab")
portfolio_tab_module = import_tab("portfolio_tab")
strategie_tab_module = import_tab("strategie_tab")
alerty_tab_module = import_tab("alerty_tab")
analityka_tab_module = import_tab("analityka_tab")
ai_tab_module = import_tab("ai_tab")

# --- Ustawienia strony ---
st.set_page_config(
    page_title="TradingRevolution - StockMatrix",
    layout="wide",
    page_icon="📊"
)

# Pasek boczny
st.sidebar.title("🚀 TradingRevolution")
st.sidebar.image("assets/logo.png", use_container_width=True)

# Menu
menu = st.sidebar.radio(
    "Wybierz zakładkę:",
    ["Akcje", "Krypto", "Portfolio", "Strategie", "Alerty", "Analityka", "AI"]
)

# --- Routing zakładek ---
if menu == "Akcje" and akcje_tab_module:
    akcje_tab_module.akcje_tab()
elif menu == "Krypto" and krypto_tab_module:
    krypto_tab_module.krypto_tab()
elif menu == "Portfolio" and portfolio_tab_module:
    portfolio_tab_module.portfolio_tab()
elif menu == "Strategie" and strategie_tab_module:
    strategie_tab_module.strategie_tab()
elif menu == "Alerty" and alerty_tab_module:
    alerty_tab_module.alerty_tab()
elif menu == "Analityka" and analityka_tab_module:
    analityka_tab_module.analityka_tab()
elif menu == "AI" and ai_tab_module:
    ai_tab_module.ai_tab()
else:
    st.info("🚧 Ta zakładka jest w budowie lub wystąpił problem z importem.")
