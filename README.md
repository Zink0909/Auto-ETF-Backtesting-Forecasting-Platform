# ETF Dollar-Cost-Averaging Backtest & Analytics

A reproducible backtest of dollar-cost-averaging (DCA) into ETFs, with
**correctly separated** money-weighted and time-weighted performance metrics and
a DCA-vs-lump-sum comparison. CLI and Streamlit front-ends share one core.

> Refactor of an earlier notebook/script that read prices from a private Google
> Sheet (with a **committed service-account key**) and computed Sharpe/CAGR on a
> series polluted by cash contributions. See [`legacy/`](legacy/README.md).

## What it does

* **Data** (`data/prices.py`) — pulls daily adjusted closes from `yfinance`,
  cached to parquet. No credentials. A deterministic `synthetic` source makes the
  whole pipeline runnable offline (tests, CI, `make demo`).
* **DCA engine** (`dca.py`) — contribution dates from a pandas calendar snapped to
  trading days (fixes the legacy "skip a month on a holiday" bug); a clean ledger.
* **Performance** (`performance.py`) — the core fix:
  * **money-weighted return (XIRR)** over the actual contribution cashflows — the
    honest "what did the DCA strategy return", and
  * **time-weighted asset metrics** (CAGR, vol, Sharpe, Sortino, max drawdown)
    computed on the *price* series, not on a market value inflated by deposits.
* **Benchmark** (`benchmark.py`) — DCA vs. lump sum on equal capital.

## The bug this fixes

The legacy `analyze_performance` computed CAGR/Sharpe/Sortino from the DCA
portfolio's **market value**. That series grows from market moves *and* from new
contributions, so the "CAGR" literally counted your deposits as investment
growth. Returns of a strategy with cashflows are a money-weighted (IRR) question;
risk metrics belong on the asset's own returns. This project keeps them separate.

## Quickstart

```bash
micromamba create -n etf-dca -f environment.yml   # or: pip install -e ".[dev]"
make demo     # offline synthetic run (no network)
make run      # real run via yfinance (configs/default.yaml)
make app      # Streamlit UI
make test     # 9 tests
```

Everything tunable (tickers, dates, contribution amount/frequency, data source)
is in `configs/default.yaml`.

## Layout

```
src/etf_dca/
  data/prices.py   yfinance + synthetic sources, parquet cache
  dca.py           DCA backtest engine
  performance.py   XIRR (money-weighted) + asset risk metrics
  benchmark.py     DCA vs lump sum
  plotting.py      figures (returned, not shown)
  run.py           CLI orchestrator + Excel/figure report
app.py             Streamlit front-end (imports the same core)
configs/ tests/ legacy/
```

## Security note

The legacy project committed a live GCP service-account private key. This rewrite
needs no credentials; if you re-add a Google-Sheets source, load the key from an
environment variable or `.streamlit/secrets.toml` (both gitignored) and **rotate
the leaked key**.

## Data source

Prices via [`yfinance`](https://github.com/ranaroussi/yfinance) (Yahoo Finance).
For research only; not investment advice.
