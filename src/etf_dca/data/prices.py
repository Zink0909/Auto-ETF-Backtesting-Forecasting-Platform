"""Reproducible ETF price data.

Replaces the legacy Google-Sheets + service-account-key dependency (which was
unreproducible and leaked a private key) with:

  * ``yfinance``   -- real public market data, cached locally as parquet, no
                      credentials required; or
  * ``synthetic``  -- a deterministic geometric-Brownian-motion generator so the
                      pipeline, tests and CI run fully offline.

Both return the same shape, so everything downstream is source-agnostic.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd


def _cache_file(cache_dir: Path, ticker: str, start: str, end: str, source: str) -> Path:
    return cache_dir / f"{source}_{ticker}_{start}_{end}.parquet"


def download_yfinance(ticker: str, start: str, end: str, retries: int = 3) -> pd.DataFrame:
    """Download daily adjusted close, retrying through transient rate limits."""
    import yfinance as yf

    last_err = None
    for attempt in range(retries):
        try:
            raw = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
            if not raw.empty:
                adj = raw["Adj Close"]
                if isinstance(adj, pd.DataFrame):
                    adj = adj.iloc[:, 0]
                out = adj.reset_index()
                out.columns = ["date", "adj_close"]
                out["date"] = pd.to_datetime(out["date"])
                return out
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"yfinance failed for {ticker} ({start}..{end}): {last_err}")


def synthetic_prices(ticker: str, start: str, end: str, seed: int = 42) -> pd.DataFrame:
    """Deterministic GBM price path on trading days -- offline stand-in for real data."""
    dates = pd.bdate_range(start=start, end=end)
    rng = np.random.default_rng(seed + (abs(hash(ticker)) % 1000))
    mu, sigma = 0.08 / 252, 0.16 / np.sqrt(252)   # ~8% drift, 16% vol annualised
    shocks = rng.normal(mu, sigma, len(dates))
    price = 100 * np.exp(np.cumsum(shocks))
    return pd.DataFrame({"date": dates, "adj_close": price})


def get_prices(ticker, start, end, cache_dir, source="yfinance", seed=42) -> pd.DataFrame:
    """Return [date, adj_close] for a ticker, using the parquet cache when present."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    f = _cache_file(cache_dir, ticker, start, end, source)
    if f.exists():
        return pd.read_parquet(f)

    if source == "synthetic":
        df = synthetic_prices(ticker, start, end, seed)
    elif source == "yfinance":
        df = download_yfinance(ticker, start, end)
    else:
        raise ValueError(f"unknown data source: {source!r}")

    df.to_parquet(f, index=False)
    return df


def price_series(df: pd.DataFrame) -> pd.Series:
    """[date, adj_close] -> Series indexed by date (sorted, de-duplicated, no NaN)."""
    s = df.set_index("date")["adj_close"].sort_index()
    return s[~s.index.duplicated(keep="last")].dropna()
