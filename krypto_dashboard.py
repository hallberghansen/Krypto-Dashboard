import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import yfinance as yf
import datetime
import requests
from ta.momentum import RSIIndicator
from ta.trend import MACD

st.set_page_config(page_title="XRP & HBAR Analyseværktøj", layout="wide")
st.title("🔎 XRP & HBAR Markedsovervågning")

# --- Valg og datohåndtering ---
selected_token = st.selectbox("Vælg kryptovaluta", ['XRP-USD', 'HBAR-USD'])
start_date = st.date_input("Startdato", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.date_input("Slutdato", datetime.date.today())

# --- Hent prisdata ---
data = yf.download(selected_token, start=start_date, end=end_date)
data.dropna(inplace=True)

if not data.empty and 'Close' in data.columns:
    try:
        # --- Teknisk analyse: RSI og MACD ---
        close_series = data['Close'].astype(float)
        data['RSI'] = RSIIndicator(close=close_series).rsi()
        macd = MACD(close=close_series)
        data['MACD'] = macd.macd()
        data['MACD_signal'] = macd.macd_signal()
    except Exception as e:
        st.error(f"🚫 Fejl ved teknisk analyse: {e}")
        st.stop()

    # --- Candlestick graf ---
    st.subheader("📈 Pris og candlestick-graf")
    candle = go.Figure(data=[
        go.Candlestick(x=data.index,
                       open=data['Open'],
                       high=data['High'],
                       low=data['Low'],
                       close=data['Close'])
    ])
    candle.update_layout(height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(candle, use_container_width=True)

    # --- RSI og MACD grafer ---
    st.subheader("📊 RSI og MACD")
    col1, col2 = st.columns(2)

    with col1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI'))
        fig_rsi.update_layout(title='RSI', height=300)
        st.plotly_chart(fig_rsi, use_container_width=True)

    with col2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD'))
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], name='Signal'))
        fig_macd.update_layout(title='MACD', height=300)
        st.plotly_chart(fig_macd, use_container_width=True)

    # --- Whale-transaktioner og TVL (dummy data) ---
    st.subheader("🐋 Whale-transaktioner og TVL")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Seneste Whale-transaktioner", "12 over 1M USD")
        st.progress(0.6)

    with col4:
        st.metric("Total Value Locked (TVL)", "$128M")
        st.progress(0.8)

    # --- Twitter sentiment (placeholder) ---
    st.subheader("💬 Twitter-sentiment og nyheder")
    st.info("Seneste tweet fra @hedera: 'HBAR når nye højder! 🚀' \n\nSentiment: Positivt ✓")
    st.info("Seneste tweet fra @Ripple: 'XRP ETF-nyheder snart? Hold øje!' \n\nSentiment: Optimistisk")

    # --- Breaking news (placeholder) ---
    st.warning("BREAKING: XRP inkluderet i Grayscale-fond. HBAR partnerskab med Lloyds Bank bekræftet.")
else:
    st.error("❌ Ingen data hentet – prøv en anden dato eller kryptovaluta.")
    st.stop()
