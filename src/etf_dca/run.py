"""CLI: run the DCA analysis over all configured tickers and write a report.

Run as:  python -m etf_dca.run
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import pandas as pd

from .benchmark import compare_dca_vs_lump_sum
from .config import Config
from .data.prices import get_prices, price_series
from .dca import simulate_dca
from .performance import asset_metrics, dca_return
from .plotting import profit_curve


def analyse_ticker(ticker: str, cfg: Config) -> dict:
    d, a = cfg["data"], cfg["analysis"]
    prices = price_series(
        get_prices(ticker, d["start"], d["end"], cfg.data_path("cache_dir"),
                   source=d["source"], seed=d["synthetic_seed"])
    )
    dca = simulate_dca(prices, cfg["dca"]["amount"], cfg["dca"]["frequency"],
                       cfg["dca"]["weekday"], cfg["dca"]["start_principal"])
    mw = dca_return(dca.cashflows)
    am = asset_metrics(prices, a["risk_free_rate"], a["trading_days"])
    return {"ticker": ticker, **dca.summary,
            "money_weighted_return_pct": mw["money_weighted_return_pct"], **am}, dca, prices


def main(cfg: Config | None = None) -> pd.DataFrame:
    cfg = cfg or Config.load()
    reports = cfg.path("reports_dir")
    (reports / "figures").mkdir(parents=True, exist_ok=True)

    rows, logs = [], {}
    for ticker in cfg["data"]["tickers"]:
        try:
            summary, dca, _ = analyse_ticker(ticker, cfg)
            rows.append(summary)
            logs[ticker] = dca.log
            profit_curve(dca.log, ticker, cfg["dca"].get("rolling")).savefig(
                reports / "figures" / f"profit_{ticker}.png", dpi=120)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {ticker}: {e}")

    summary_df = pd.DataFrame(rows)
    pd.set_option("display.width", 160)
    print(summary_df.to_string(index=False))

    with pd.ExcelWriter(reports / "investment_report.xlsx", engine="xlsxwriter") as xl:
        summary_df.to_excel(xl, sheet_name="Summary", index=False)
        for t, log in logs.items():
            log.to_excel(xl, sheet_name=f"{t}_log", index=False)
    print(f"\nwrote {reports / 'investment_report.xlsx'}")
    return summary_df


if __name__ == "__main__":
    main()
