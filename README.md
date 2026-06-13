# ETF Dollar-Cost-Averaging Backtest & Analytics

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![tests](https://img.shields.io/badge/tests-9%20passing-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

A reproducible backtest of **dollar-cost averaging (DCA)** into ETFs, with
**correctly separated** money-weighted and time-weighted performance metrics, a
DCA-vs-lump-sum comparison, and a Streamlit UI. CLI and app share one core.

> **TL;DR** — A prior version computed Sharpe / CAGR from the portfolio's
> **market value**, which grows from market moves *and* from your own
> contributions — so the "CAGR" literally counted deposits as investment growth.
> It also read prices from a private Google Sheet behind a **committed
> service-account key**. This rewrite fixes the metrics, removes the credential,
> and runs from public data (or fully offline).

## The bug this fixes

Returns of a strategy with cashflows are a **money-weighted (IRR)** question; risk
metrics belong on the **asset's own returns**. The legacy code mixed them by
computing everything on a contribution-inflated market-value series. This project
keeps them separate and reports three distinct, correct numbers:

| metric | question it answers | computed on |
|---|---|---|
| **total return %** | how much did I make in total? | invested vs. final value |
| **money-weighted return (XIRR)** | what annualized rate did *my contributions* earn? | the dated cashflow stream |
| **asset CAGR / vol / Sharpe / Sortino / max DD** | what are the *asset's* risk/return traits? | the price series (no contributions) |

## What it does

- **Data** (`data/prices.py`) — daily adjusted closes from `yfinance`, cached to
  parquet, **no credentials**. A deterministic `synthetic` source makes the whole
  pipeline runnable offline (tests, CI, `make demo`).
- **DCA engine** (`dca.py`) — contribution dates from a pandas calendar snapped to
  trading days (fixes a legacy "skip a month on a holiday" bug); a clean ledger.
- **Performance** (`performance.py`) — XIRR + asset risk metrics, kept separate.
- **Benchmark** (`benchmark.py`) — **DCA vs. lump sum** on equal capital (the
  classic "is averaging in actually better?" question).
- **Front-ends** — a CLI report (`run.py`) and a **Streamlit app** (`app.py`) that
  import the *same* core (the legacy app re-implemented all the logic separately).

## Quickstart

```bash
micromamba create -n etf-dca -f environment.yml   # or: pip install -e ".[dev]"
make demo     # offline synthetic run — no network, runs anywhere
make run      # real run via yfinance (edit configs/default.yaml)
make app      # Streamlit UI
make test     # 9 tests
```

All tunables (tickers, dates, contribution amount/frequency, data source) live in
`configs/default.yaml`.

## What this demonstrates

Backtesting design · money-weighted vs. time-weighted return (IRR/XIRR) ·
risk-adjusted metrics (Sharpe, Sortino, max drawdown) · reproducible data
pipelines & caching · secure credential handling · one core behind a CLI and a
Streamlit app · unit tests & CI.

## Layout

```
src/etf_dca/
  data/prices.py   yfinance + offline synthetic sources, parquet cache
  dca.py           DCA backtest engine
  performance.py   XIRR (money-weighted) + asset risk metrics
  benchmark.py     DCA vs lump sum
  plotting.py      figures (returned, not shown)
  run.py           CLI orchestrator + Excel/figure report
app.py             Streamlit front-end (imports the same core)
configs/  tests/
```

## Security note

The legacy project committed a live GCP service-account private key. This rewrite
needs none; `.gitignore` blocks `*.json` and secrets. If you add a Google-Sheets
source, load the key from an environment variable or `.streamlit/secrets.toml`
(both gitignored) — and rotate any previously-exposed key.

Prices via [`yfinance`](https://github.com/ranaroussi/yfinance). For research /
portfolio purposes only — not investment advice. MIT licensed.
