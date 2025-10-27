import streamlit as st
import requests
import datetime

alerts = {}
alerts_history = []

TELEGRAM_TOKEN = "TWÓJ_TOKEN"
TELEGRAM_CHAT_ID = "TWÓJ_CHAT_ID"

def set_alert(ticker, price):
    alerts[ticker] = price
    st.success(f"Alert ustawiony: {ticker} przy ${price}")

def check_alerts(current_prices):
    for ticker, price in current_prices.items():
        if ticker in alerts and price >= alerts[ticker]:
            st.warning(f"⚠️ Alert: {ticker} osiągnął ${price}!")
            send_telegram(f"Alert: {ticker} osiągnął ${price}!")
            alerts_history.append({"ticker":ticker, "price":price, "time":datetime.datetime.now()})

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    requests.get(url)
