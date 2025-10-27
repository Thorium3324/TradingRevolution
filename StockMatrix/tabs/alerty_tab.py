import streamlit as st
from utils.alerts import check_alerts

def alerty_tab():
    st.title("🚨 Alerty")
    symbol = st.text_input("Symbol:", "AAPL")
    if st.button("Sprawdź alerty"):
        alerts = check_alerts(symbol)
        for a in alerts:
            st.warning(a)
