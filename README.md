# 📈 ETF-Prophet: Automated ETF Analysis, Forecasting & Strategy Simulation

**ETF-Prophet** is an end-to-end ETF analytics engine built in Jupyter Notebook. It integrates real-time data acquisition via custom web crawlers, automated updates to Google Sheets, and statistical modeling for short-term trend forecasting. The project also supports user-configurable investment strategies and performance evaluation across multiple ETFs.

---

## 🚀 Key Features

### 🔄 Real-Time ETF Data Pipeline
- Custom ETF crawler scrapes up-to-date price data from web sources
- Google Sheets automatically syncs historical data via Sheets API (OAuth2)
- Supports reproducible analysis and strategy testing without manual data handling

### 📊 Strategy-Driven Investment Simulator
- Implements configurable strategies such as:
  - SMA Crossover
  - Mean Reversion
- Simulates portfolio growth over custom periods and tickers
- Visualizes equity curves and annotated buy/sell signals

### 📐 Quantitative Metrics & Analytics
- Computes Sharpe Ratio, CAGR, Max Drawdown, Sortino Ratio, and Volatility
- Visual summary of return distributions and rolling volatility
- Multi-ETF backtesting with comparative performance plots

### 🔮 Short-Term Forecasting with Prophet
- Applies Facebook Prophet to model ETF price movement
- Constructs rolling confidence intervals and prediction bands
- Provides trend insight for near-future movements

---

## 📂 Project Structure

```
ETF-Prophet/
├── etf_scraper.py
├── google_sheets_updater.py
├── strategy_simulation.ipynb
├── prophet_forecasting.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🧰 Tech Stack

- `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`
- `requests`, `BeautifulSoup` for scraping
- `gspread`, `oauth2client` for Sheets API
- `fbprophet` for forecasting
- `ipywidgets` for notebook interactivity

---

## 📈 Use Cases

- Backtest ETF strategies with auto-updated data
- Forecast short-term price trends
- Compare ETFs using return metrics and volatility analysis
- Share reproducible dashboards via Google Sheets

---

## 🔐 Requirements

- Google Cloud credentials (OAuth2) for Sheets API access
- Python ≥ 3.7
- All dependencies listed in `requirements.txt`

---

## 📌 Future Work

- Add benchmark comparisons (e.g., SPY, QQQ)
- Extend to portfolio-level optimization
- Deploy Streamlit dashboard or Google App Script interface