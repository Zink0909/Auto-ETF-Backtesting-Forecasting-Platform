# Legacy versions — kept for provenance

The original project existed twice (a Jupyter notebook and a `Invest python/`
script package) implementing the same ETF DCA + Prophet-forecast logic. They are
not copied here verbatim on purpose — `app.py` hard-coded a service-account key
filename, and copying it would spread that pattern. This note records what the
refactor changed and why.

| Problem in the legacy version | Fix in the rewrite |
|---|---|
| **Live GCP service-account private key committed** in the repo, referenced by `config.py` and hard-coded in `app.py` | No credentials; `yfinance` public data. `.gitignore` blocks `*.json`/secrets; README says rotate the leaked key |
| **Sharpe/CAGR/Sortino computed on portfolio market value** — which includes cash contributions, so the metrics counted deposits as returns | `performance.py` separates **money-weighted XIRR** (strategy) from **time-weighted asset metrics** (on price returns) |
| **Data from a private Google Sheet** via gspread — slow, unreproducible, needs the key | `yfinance` → parquet cache; deterministic `synthetic` source for offline runs |
| **`app.py` re-implemented** `simulate_dca` + forecast (a worse copy) | Streamlit app imports the same core; one implementation |
| **Prophet "forecast" of ETF prices** with no backtest/validation | Removed — prices are near-efficient; the project focuses on a sound DCA backtest instead |
| Convoluted day-by-day date loop that could skip a month on holidays | Calendar-based contribution dates snapped to trading days |
| Unpinned `requirements.txt`, no tests, output committed | Installable package, pinned env, 9 tests, Makefile |

The two original folders (`Invest/` notebook and `Invest python/`) remain in the
parent directory. **Delete the service-account JSON files from them and rotate
the key.**
