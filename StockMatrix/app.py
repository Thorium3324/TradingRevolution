import streamlit as st

# --- Import zakładek ---
try:
    from tabs.akcje_tab import akcje_tab
except ImportError:
    def akcje_tab():
        st.warning("Zakładka Akcje niedostępna.")

try:
    from tabs.krypto_tab import krypto_tab
except ImportError:
    def krypto_tab():
        st.warning("Zakładka Krypto niedostępna.")

# --- Konfiguracja strony ---
st.set_page_config(
    page_title="TradingRevolution Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("TradingRevolution Ultimate")

# --- Zakładki ---
tab_options = ["AI", "Alerty", "Analityka", "Strategie"]
tabs = st.tabs(tab_options)

# --- AI ---
with tabs[0]:
    st.subheader("Zakładka AI")
    try:
        st.info("Tutaj będzie logika AI i predykcji.")
    except Exception as e:
        st.error(f"Błąd w zakładce AI: {e}")

# --- Alerty ---
with tabs[1]:
    st.subheader("Zakładka Alerty")
    try:
        st.info("Tutaj będzie logika alertów i powiadomień.")
    except Exception as e:
        st.error(f"Błąd w zakładce Alerty: {e}")

# --- Analityka ---
with tabs[2]:
    st.subheader("Zakładka Analityka")
    try:
        # Wywołanie zakładki Akcje
        akcje_tab()
    except Exception as e:
        st.error(f"Błąd w zakładce Analityka: {e}")

# --- Strategie ---
with tabs[3]:
    st.subheader("Zakładka Strategie")
    try:
        # Tutaj możesz załadować np. strategię inwestycyjną
        st.info("Tutaj będzie logika strategii.")
    except Exception as e:
        st.error(f"Błąd w zakładce Strategie: {e}")
