import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date
from plotly import graph_objs as go

from promoter import fetch_promoter_holding, compute_signal

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.set_page_config(page_title="pyStocks+", layout="wide")
st.title("pyStocks+")
st.caption("Buy/sell signal from promoter shareholding trend")

symbol = st.text_input("NSE stock symbol (e.g. TCS, RELIANCE, INFY)", "TCS").strip().upper()


@st.cache_data(ttl=3600)
def load_price(ticker):
    data = yf.download(f"{ticker}.NS", start=START, end=TODAY)
    data.reset_index(inplace=True)
    return data


data = load_price(symbol)
if data.empty:
    st.error(f"No price data found for {symbol}.NS — check the symbol.")
    st.stop()

st.subheader("Price")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Date"], y=data["Open"], name="Open"))
fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close"))
fig.layout.update(xaxis_rangeslider_visible=True)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(data.tail())

st.subheader("Promoter shareholding signal")
try:
    holding_df = fetch_promoter_holding(symbol)
    if holding_df.empty:
        raise ValueError("NSE returned no shareholding data")
except Exception:
    st.warning(
        "Live NSE fetch failed for this symbol/host right now. "
        "Enter the last two quarterly promoter holding % manually, e.g. from screener.in or NSE's site."
    )
    col1, col2 = st.columns(2)
    prev_pct = col1.number_input("Previous quarter promoter holding %", 0.0, 100.0, 50.0)
    latest_pct = col2.number_input("Latest quarter promoter holding %", 0.0, 100.0, 50.0)
    holding_df = pd.DataFrame({"promoter_pct": [prev_pct, latest_pct]})

signal, delta = compute_signal(holding_df)
color = {"BUY": "green", "SELL": "red", "HOLD": "gray"}[signal]
st.markdown(f"## :{color}[{signal}]  (Δ promoter holding: {delta:+.2f}%)")

if "quarter" in holding_df.columns:
    st.line_chart(holding_df.set_index("quarter")["promoter_pct"])
    st.dataframe(holding_df)
