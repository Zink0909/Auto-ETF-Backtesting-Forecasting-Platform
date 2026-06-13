"""Plotting helpers. Functions return a Figure so both the CLI and the Streamlit
app can reuse them without side effects (no implicit plt.show())."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def profit_curve(log: pd.DataFrame, label: str, rolling: int | None = None):
    df = log.copy()
    df["profit_pct"] = (df["market_value"] / df["total_invested"] - 1) * 100
    y = df["profit_pct"]
    if rolling and rolling > 1:
        y = y.rolling(rolling, min_periods=1).mean()
        label = f"{label} (rolling {rolling})"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], y, marker="o", ms=3, label=label)
    ax.axhline(0, color="k", lw=0.8, ls="--")
    ax.set(title="DCA profit over time", xlabel="Date", ylabel="Profit (%)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def dca_vs_lumpsum_bar(comparison: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(comparison["strategy"], comparison["total_return_pct"],
           color=["#4C72B0", "#DD8452"])
    ax.set(title="DCA vs lump sum", ylabel="Total return (%)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig
