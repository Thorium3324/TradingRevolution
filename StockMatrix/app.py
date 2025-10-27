# app.py
import streamlit as st
from tabs.akcje_tab import akcje_tab

# --------------------------
# Ustawienia strony
# --------------------------
st.set_page_config(
    page_title="Trading Revolution",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Trading Revolution")

# Jeśli nie masz już logo, usuń obrazek lub zastąp tekstem
# st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.markdown("### 🚀 TradingRevolution")

# --------------------------
# Zakładki
# --------------------------
st.title("Trading Revolution Dashboard")

tabs = ["Akcje"]  # Dodajemy kolejne zakładki później: "Krypto", "Portfolio", "Strategie" itd.
selected_tab = st.sidebar.radio("Wybierz zakładkę:", tabs)

# --------------------------
# Wywołanie zakładek
# --------------------------
if selected_tab == "Akcje":
    akcje_tab()

# Tutaj w przyszłości możemy dodać np.
# elif selected_tab == "Krypto":
#     krypto_tab()
# elif selected_tab == "Portfolio":
#     portfolio_tab()
# elif selected_tab == "Strategie":
#     strategie_tab()
