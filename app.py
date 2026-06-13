"""Streamlit front-end. Thin: it imports the same core as the CLI -- no
re-implemented DCA or metrics logic (the legacy app.py duplicated all of it).

Run:  streamlit run app.py
"""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from etf_dca.benchmark import compare_dca_vs_lump_sum
from etf_dca.data.prices import get_prices, price_series
from etf_dca.dca import simulate_dca
from etf_dca.performance import asset_metrics, dca_return
from etf_dca.plotting import dca_vs_lumpsum_bar, profit_curve

st.set_page_config(page_title="ETF DCA Simulator", layout="centered")
st.title("📈 ETF Dollar-Cost-Averaging Simulator")

with st.sidebar:
    ticker = st.text_input("Ticker", "SPY").upper()
    source = st.selectbox("Data source", ["yfinance", "synthetic"])
    start = st.date_input("Start", pd.to_datetime("2018-01-01"))
    end = st.date_input("End", pd.to_datetime("2024-12-31"))
    amount = st.slider("Contribution per period ($)", 50, 1000, 200, step=50)
    frequency = st.selectbox("Frequency", ["monthly", "weekly", "biweekly", "daily"])
    start_principal = st.number_input("Initial lump sum ($)", 0, 100_000, 0, step=500)


@st.cache_data
def load(ticker, start, end, source):
    return price_series(get_prices(ticker, str(start), str(end), "data/cache", source=source))


try:
    prices = load(ticker, start, end, source)
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load {ticker}: {e}")
    st.stop()

dca = simulate_dca(prices, amount, frequency, start_principal=start_principal)
mw = dca_return(dca.cashflows)
am = asset_metrics(prices)

c1, c2, c3 = st.columns(3)
c1.metric("Total invested", f"${dca.summary['total_invested']:,.0f}")
c2.metric("Final value", f"${dca.summary['final_value']:,.0f}")
c3.metric("Money-weighted return", f"{mw['money_weighted_return_pct']:.2f}%/yr")

st.subheader("Asset risk metrics (time-weighted, on the price series)")
st.write(am)

st.subheader("Profit over time")
st.pyplot(profit_curve(dca.log, ticker))

st.subheader("DCA vs lump sum (same capital)")
cmp = compare_dca_vs_lump_sum(prices, amount, frequency, start_principal=start_principal)
st.dataframe(cmp, hide_index=True)
st.pyplot(dca_vs_lumpsum_bar(cmp))

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as xl:
    pd.DataFrame([dca.summary]).to_excel(xl, sheet_name="Summary", index=False)
    dca.log.to_excel(xl, sheet_name="Log", index=False)
st.download_button("📥 Download Excel report", buffer.getvalue(), f"{ticker}_dca_report.xlsx")
