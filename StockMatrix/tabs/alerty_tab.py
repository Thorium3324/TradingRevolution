import streamlit as st
from utils.alerts import check_alerts

def alerty_tab():
    st.title("🔔 Alerty")
    msg = check_alerts()
    st.success(msg)
