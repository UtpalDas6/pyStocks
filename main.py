import csv
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date
from plotly import graph_objs as go

from promoter import fetch_promoter_holding, compute_signal
from lookup import resolve_symbol

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.set_page_config(page_title="pyStocks+", layout="centered")
st.title("pyStocks+")
st.write(
    "Type an NSE stock symbol or company name. This checks whether the "
    "company's promoters (its founders/owners) have been buying or selling "
    "their own shares recently — that's usually a signal worth watching."
)

with open("nifty50.csv") as f:
    NIFTY50 = [(row["symbol"], row["name"]) for row in csv.DictReader(f)]
OPTIONS = [f"{sym} — {name}" for sym, name in NIFTY50]
SYMBOL_BY_OPTION = {f"{sym} — {name}": sym for sym, name in NIFTY50}

choice = st.selectbox(
    "Stock symbol or company name",
    OPTIONS,
    index=next(i for i, (sym, _) in enumerate(NIFTY50) if sym == "TCS"),
    accept_new_options=True,
    help="Pick a suggestion or type any NSE symbol/company name",
)
query = SYMBOL_BY_OPTION.get(choice, choice)


@st.cache_data(ttl=3600)
def cached_resolve_symbol(q):
    return resolve_symbol(q)


symbol = cached_resolve_symbol(query)
if symbol is None:
    st.error(f"Couldn't find '{query}' on NSE — try the exact symbol (e.g. INFY) or the fuller company name.")
    st.stop()
if symbol.upper() != query.strip().upper():
    st.caption(f"Matched to NSE symbol: **{symbol}**")


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
