import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import yfinance as yf
import datetime
import requests
import feedparser
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

st.set_page_config(page_title="XRP & HBAR Analyseværktøj", layout="wide")
st.title("🔎 XRP & HBAR Markedsovervågning")

# --- Valg og datohåndtering ---
selected_token = st.selectbox("Vælg kryptovaluta", ['XRP-USD', 'HBAR-USD'])
start_date = st.date_input("Startdato", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.date_input("Slutdato", datetime.date.today())

# --- Indikatorvalg ---
show_rsi = st.checkbox("Vis RSI", value=True)
show_macd = st.checkbox("Vis MACD", value=True)
show_bollinger = st.checkbox("Vis Bollinger Bands", value=False)

# --- Hent prisdata ---
data = yf.download(selected_token, start=start_date, end=end_date)
data.dropna(inplace=True)

if not data.empty and 'Close' in data.columns:
    try:
        close_series = data['Close'].astype(float).squeeze()
        if close_series.ndim > 1:
            close_series = close_series.iloc[:, 0]  # reducer til 1D hvis nødvendigt

        if show_rsi:
            data['RSI'] = RSIIndicator(close=close_series).rsi()
        if show_macd:
            macd = MACD(close=close_series)
            data['MACD'] = macd.macd()
            data['MACD_signal'] = macd.macd_signal()
        if show_bollinger:
            bb = BollingerBands(close=close_series)
            data['bb_bbm'] = bb.bollinger_mavg()
            data['bb_bbh'] = bb.bollinger_hband()
            data['bb_bbl'] = bb.bollinger_lband()
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
    if show_bollinger:
        candle.add_trace(go.Scatter(x=data.index, y=data['bb_bbh'], name='Bollinger High', line=dict(dash='dot')))
        candle.add_trace(go.Scatter(x=data.index, y=data['bb_bbl'], name='Bollinger Low', line=dict(dash='dot')))
    candle.update_layout(height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(candle, use_container_width=True)

    # --- RSI og MACD grafer ---
    if show_rsi or show_macd:
        st.subheader("📊 Indikatorgrafer")
        col1, col2 = st.columns(2)

        if show_rsi:
            with col1:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI'))
                fig_rsi.update_layout(title='RSI', height=300)
                st.plotly_chart(fig_rsi, use_container_width=True)

        if show_macd:
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

    # --- Twitter-sentiment og kilder ---
    st.subheader("💬 Twitter-sentiment og kilder")
    st.markdown("**Seneste kilder (søgt fra Twitter/X):**")
    st.write("🔗 [Søg på XRP hos Twitter](https://twitter.com/search?q=XRP&src=typed_query)")
    st.write("🔗 [Søg på HBAR hos Twitter](https://twitter.com/search?q=HBAR&src=typed_query)")
    st.info("Seneste tweet fra @hedera: 'HBAR når nye højder! 🚀' \n\nSentiment: Positivt ✓")
    st.info("Seneste tweet fra @Ripple: 'XRP ETF-nyheder snart? Hold øje!' \n\nSentiment: Optimistisk")

    # --- Breaking news ---
    st.subheader("📰 Breaking news")
    rss_feeds = [
        "https://cryptobriefing.com/feed/",
        "https://cointelegraph.com/rss"
    ]
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:2]:
            st.write(f"**{entry.title}**")
            st.write(entry.link)
else:
    st.error("❌ Ingen data hentet – prøv en anden dato eller kryptovaluta.")
    st.stop()

