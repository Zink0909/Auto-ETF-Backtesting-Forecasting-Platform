import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
import numpy as np
import io
import gspread
from google.oauth2.service_account import Credentials

# ----------- Google Sheets Auth Configuration -----------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("etf-data-access-435896d96122.json", scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open("ETF Tracker")

# ----------- Streamlit Page Setup -----------
st.set_page_config(page_title="ETF DCA Simulator", layout="centered")
st.title("📈 ETF Dollar-Cost Averaging (DCA) Simulator")

# ----------- Sidebar Inputs -----------
ETF_LIST = ["SPY", "QQQ", "VOO","IVV","VEA","VTI","IWM","DIA","EFA","VTV","BND","AGG","VNQ","XLF","XLK",
            "XLY","XLE","XLV","XLI","XLC","XLU","XBI","ARKK","ARKG","ARKF","SOXX","SMH","VUG","VYM","TIP"]
FREQ_OPTIONS = ["monthly", "weekly", "daily", "biweekly"]

etf = st.sidebar.selectbox("Select ETF", ETF_LIST)
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))
invest_amount = st.sidebar.slider("Investment per Period ($)", 100, 1000, 200, step=50)
frequency = st.sidebar.selectbox("Investment Frequency", FREQ_OPTIONS)
rolling_window = st.sidebar.slider("Rolling Average Window", 1, 20, 5)

# ----------- Load Data -----------
@st.cache_data
def load_data(etf):
    df = pd.DataFrame(spreadsheet.worksheet(etf).get_all_records())
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data(etf)

# ----------- DCA Simulation Function -----------
def simulate_dca(df, start_date, end_date, invest_amount,
                 frequency='weekly', weekday=0, start_principal=0, log=False):
    df = df.copy()
    df = df.dropna(subset=["Adj Close"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

    trading_dates = df_filtered["Date"].tolist()
    current_date = pd.to_datetime(start_date)
    invest_dates = []
    last_added = None

    while current_date <= pd.to_datetime(end_date):
        if frequency == "daily":
            invest_dates.append(current_date)
        elif frequency == "weekly" and current_date.weekday() == weekday:
            invest_dates.append(current_date)
        elif frequency == "biweekly" and current_date.weekday() == weekday:
            if not last_added or (current_date - last_added).days >= 14:
                invest_dates.append(current_date)
                last_added = current_date
        elif frequency == "monthly" and current_date.weekday() == weekday:
            if not last_added or current_date.month != last_added.month:
                invest_dates.append(current_date)
                last_added = current_date
        current_date += pd.Timedelta(days=1)

    actual_invest_dates = [min([d for d in trading_dates if d >= inv], default=None) for inv in invest_dates]
    actual_invest_dates = list(filter(None, actual_invest_dates))

    total_invested = 0
    total_shares = 0
    log_data = []

    for date in actual_invest_dates:
        row = df_filtered[df_filtered["Date"] == date]
        if not row.empty:
            price = row["Adj Close"].values[0]
            shares = invest_amount / price
            total_invested += invest_amount
            total_shares += shares
            if log:
                log_data.append({
                    "Date": date,
                    "Price": price,
                    "Shares": shares,
                    "Total Shares": total_shares,
                    "Total Invested": total_invested,
                    "Market Value": total_shares * price
                })

    final_price = df_filtered.iloc[-1]["Adj Close"]
    final_value = total_shares * final_price
    total_return = final_value - total_invested

    result = {
        "Total Invested": round(total_invested, 2),
        "Total Shares": round(total_shares, 4),
        "Final Value": round(final_value, 2),
        "Total Return ($)": round(total_return, 2),
        "Total Return (%)": round((total_return / total_invested) * 100, 2)
    }

    return result, pd.DataFrame(log_data)

# ----------- Prophet Forecast Function -----------
def forecast_prices_with_prophet(df, periods=30, etf_name="ETF"):
    prophet_df = df[['Date', 'Adj Close']].rename(columns={'Date': 'ds', 'Adj Close': 'y'})
    model = Prophet(daily_seasonality=False)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast, model

# ----------- Run Simulation & Show Results -----------
result, log_df = simulate_dca(df, start_date, end_date, invest_amount, frequency, log=True)
st.subheader("📊 Simulation Result")
st.write(result)

# ----------- Profit Plot -----------
st.subheader("📈 Profit Trend")
log_df["Profit (%)"] = (log_df["Market Value"] / log_df["Total Invested"] - 1) * 100
log_df["Smoothed"] = log_df["Profit (%)"].rolling(window=rolling_window, min_periods=1).mean()

fig1, ax = plt.subplots()
ax.plot(log_df["Date"], log_df["Smoothed"], label=f"{etf} (Rolling {rolling_window})", marker='o')
ax.set_title("Profit Percentage Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Profit (%)")
ax.grid(True)
ax.legend()
st.pyplot(fig1)

# ----------- Forecast Plot -----------
st.subheader("🔮 ETF Price Forecast (Prophet)")
forecast_df, model = forecast_prices_with_prophet(df)
fig2 = model.plot(forecast_df)
plt.title(f"{etf} Price Forecast")
st.pyplot(fig2)

# ----------- Excel Export -----------
st.subheader("📥 Export Excel Report")
if st.button("Export"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        pd.DataFrame([result]).to_excel(writer, sheet_name="Summary", index=False)
        log_df.to_excel(writer, sheet_name="Log", index=False)
        forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_excel(writer, sheet_name="Forecast", index=False)
    st.download_button(
        label="Click to Download Excel File",
        data=buffer,
        file_name=f"{etf}_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
