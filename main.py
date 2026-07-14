import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date
from plotly import graph_objs as go

from promoter import fetch_promoter_holding, compute_signal

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.set_page_config(page_title="pyStocks+", layout="centered")
st.title("pyStocks+")
st.write(
    "Type an NSE stock symbol. This checks whether the company's promoters "
    "(its founders/owners) have been buying or selling their own shares "
    "recently — that's usually a signal worth watching."
)

symbol = st.text_input("Stock symbol", "TCS", help="e.g. TCS, RELIANCE, INFY").strip().upper()


@st.cache_data(ttl=3600)
def load_price(ticker):
    data = yf.download(f"{ticker}.NS", start=START, end=TODAY)
    data.reset_index(inplace=True)
    return data


data = load_price(symbol)
if data.empty:
    st.error(f"Couldn't find '{symbol}' on NSE — check the spelling.")
    st.stop()

try:
    holding_df = fetch_promoter_holding(symbol)
    if holding_df.empty:
        raise ValueError("NSE returned no shareholding data")
except Exception:
    st.info(
        f"Couldn't fetch promoter data for {symbol} automatically right now. "
        "Enter it yourself — check screener.in or NSE's shareholding pattern page."
    )
    col1, col2 = st.columns(2)
    prev_pct = col1.number_input("Promoter holding last quarter (%)", 0.0, 100.0, 50.0)
    latest_pct = col2.number_input("Promoter holding this quarter (%)", 0.0, 100.0, 50.0)
    holding_df = pd.DataFrame({"promoter_pct": [prev_pct, latest_pct]})

signal, delta = compute_signal(holding_df)

VERDICT = {
    "BUY": ("🟢 BUY", "Promoters increased their stake"),
    "SELL": ("🔴 SELL", "Promoters reduced their stake"),
    "HOLD": ("⚪ HOLD", "No meaningful change in promoter stake"),
}
label, explanation = VERDICT[signal]
st.header(label)
st.write(f"{explanation} by {abs(delta):.2f} percentage points last quarter." if delta else explanation + ".")

st.subheader(f"{symbol} price")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close price"))
fig.layout.update(xaxis_rangeslider_visible=True, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

if "quarter" in holding_df.columns:
    st.subheader("Promoter holding over time")
    st.line_chart(holding_df.set_index("quarter")["promoter_pct"])

with st.expander("Show raw data"):
    st.write("Recent price data")
    st.dataframe(data.tail())
    st.write("Promoter holding by quarter")
    st.dataframe(holding_df)
