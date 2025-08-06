# Auto-ETF-Backtesting-Forecasting-Platform: Automated ETF Analysis, Forecasting & Strategy Simulation

**Auto-ETF-Backtesting-Forecasting-Platform** is a fully automated Python-based pipeline for ETF strategy simulation, performance analytics, and short-term forecasting.

It integrates live ETF data collection via custom web crawlers, automated data synchronization to Google Sheets, and configurable investment simulations driven by flexible Python scripts. The system supports real-time strategy testing, comprehensive metric evaluation (e.g., Sharpe ratio, max drawdown), and statistical forecasting using Prophet.

Additionally, an interactive front-end interface allows users to select ETFs, adjust parameters (e.g., start/end date, investment amount, frequency), and visualize results with dynamic plots, making this tool ideal for both analysis and demonstration.


---

## Key Features

### Real-Time ETF Data Pipeline
- Custom ETF crawler scrapes up-to-date price data from web sources
- Google Sheets automatically syncs historical data via Sheets API (OAuth2)
- Supports reproducible analysis and strategy testing without manual data handling

### Strategy-Driven Investment Simulator
- Implements configurable strategies such as:
  - SMA Crossover
  - Mean Reversion
- Simulates portfolio growth over custom periods and tickers
- Visualizes equity curves and annotated buy/sell signals

### Quantitative Metrics & Analytics
- Computes Sharpe Ratio, CAGR, Max Drawdown, Sortino Ratio, and Volatility
- Visual summary of return distributions and rolling volatility
- Multi-ETF backtesting with comparative performance plots

### Short-Term Forecasting with Prophet
- Applies Facebook Prophet to model ETF price movement
- Constructs rolling confidence intervals and prediction bands
- Provides trend insight for near-future movements

### Interactive Web Interface
- Simple front-end web UI to simulate ETF strategies with custom parameters
- Users can select ETF ticker, date range, investment amount, and frequency
- Real-time visualization of performance, metrics, and forecasts


---

## Tech Stack

- `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`
- `requests`, `BeautifulSoup` for scraping
- `gspread`, `oauth2client` for Sheets API
- `fbprophet` for forecasting
- `ipywidgets` for notebook interactivity

---

## Use Cases

- Backtest ETF strategies with auto-updated data
- Forecast short-term price trends
- Compare ETFs using return metrics and volatility analysis
- Share reproducible dashboards via Google Sheets

---

### Interactive Web Interface
This project includes a lightweight interactive front-end (e.g., Streamlit or Flask) allowing users to:

- Select one or more ETFs
- Choose investment start/end date, amount, and frequency
- Toggle strategies and forecasting options
- View real-time visualizations including equity curves, prediction intervals, and metric comparisons

Ideal for demonstrating how strategy and forecast models respond to different market scenarios.


## Requirements

- Google Cloud credentials (OAuth2) for Sheets API access
- Python ≥ 3.7
- All dependencies listed in `requirements.txt`

---

## 📌 Future Work

- Add benchmark comparisons (e.g., SPY, QQQ)
- Extend to portfolio-level optimization
- Deploy Streamlit dashboard or Google App Script interface
