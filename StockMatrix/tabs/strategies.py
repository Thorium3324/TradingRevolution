import streamlit as st
from utils.strategies import moving_average_strategy

def strategie_tab():
    st.title("⚙️ Strategie")
    symbol = st.text_input("Symbol:", "AAPL")
    short = st.slider("Szybka średnia", 5, 50, 10)
    long = st.slider("Wolna średnia", 20, 200, 50)
    if st.button("Uruchom strategię MA"):
        moving_average_strategy(symbol, short, long)

