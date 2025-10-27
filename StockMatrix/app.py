import streamlit as st
from tabs import akcje_tab  # upewnij się, że masz folder tabs z plikiem akcje_tab.py

st.set_page_config(
    page_title="TradingRevolution Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("TradingRevolution Ultimate 🚀")

# --- Panel boczny ---
st.sidebar.header("Ustawienia aplikacji")
tab_choice = st.sidebar.radio("Wybierz zakładkę:", ["Akcje", "Krypto"])

# --- Odświeżanie danych ---
if st.sidebar.button("Odśwież dane"):
    st.experimental_rerun()

# --- Wywołanie odpowiedniej zakładki ---
if tab_choice == "Akcje":
    akcje_tab.akcje_tab()
elif tab_choice == "Krypto":
    st.warning("Zakładka Krypto nie została jeszcze przygotowana")
