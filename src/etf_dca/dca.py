"""Dollar-cost-averaging backtest engine.

A clean rewrite of the legacy day-by-day ``while`` loop. Contribution dates are
generated with pandas calendars and snapped to the next available trading day,
which removes the legacy "skip a month if the weekday is a holiday" bug.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

_WEEKDAY_CODE = {0: "MON", 1: "TUE", 2: "WED", 3: "THU", 4: "FRI"}


def _snap_to_trading_day(scheduled: pd.DatetimeIndex, index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Map each scheduled date to the first trading day on or after it."""
    pos = index.searchsorted(scheduled, side="left")
    pos = pos[pos < len(index)]
    return pd.DatetimeIndex(index[pos]).unique()


def contribution_dates(index: pd.DatetimeIndex, frequency: str, weekday: int = 0) -> pd.DatetimeIndex:
    """Trading days on which a contribution is made, for the given schedule."""
    start, end = index.min(), index.max()
    if frequency == "daily":
        return index
    if frequency == "monthly":
        sched = pd.date_range(start, end, freq="MS")          # month starts
    elif frequency in ("weekly", "biweekly"):
        sched = pd.date_range(start, end, freq=f"W-{_WEEKDAY_CODE[weekday]}")
        if frequency == "biweekly":
            sched = sched[::2]
    else:
        raise ValueError(f"unknown frequency: {frequency!r}")
    return _snap_to_trading_day(sched, index)


@dataclass
class DcaResult:
    log: pd.DataFrame                 # per-contribution ledger
    cashflows: list[tuple[pd.Timestamp, float]]  # for money-weighted return (XIRR)
    summary: dict[str, float]


def simulate_dca(
    prices: pd.Series,
    amount: float,
    frequency: str = "monthly",
    weekday: int = 0,
    start_principal: float = 0.0,
) -> DcaResult:
    """Backtest a DCA strategy on a price series (indexed by date)."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    prices = prices.sort_index()
    index = pd.DatetimeIndex(prices.index)

    dates = contribution_dates(index, frequency, weekday)
    rows, cashflows = [], []
    total_shares = total_invested = 0.0

    if start_principal > 0 and len(dates):
        p0 = float(prices.loc[dates[0]])
        sh = start_principal / p0
        total_shares += sh
        total_invested += start_principal
        cashflows.append((dates[0], -start_principal))
        rows.append(_row(dates[0], p0, start_principal, sh, total_shares, total_invested))

    for d in dates:
        price = float(prices.loc[d])
        sh = amount / price
        total_shares += sh
        total_invested += amount
        cashflows.append((d, -amount))
        rows.append(_row(d, price, amount, sh, total_shares, total_invested))

    final_date = index[-1]
    final_price = float(prices.iloc[-1])
    final_value = total_shares * final_price
    cashflows.append((final_date, final_value))   # liquidate at the end

    summary = {
        "total_invested": round(total_invested, 2),
        "total_shares": round(total_shares, 6),
        "final_price": round(final_price, 4),
        "final_value": round(final_value, 2),
        "total_return": round(final_value - total_invested, 2),
        "total_return_pct": round((final_value / total_invested - 1) * 100, 2),
    }
    return DcaResult(pd.DataFrame(rows), cashflows, summary)


def _row(date, price, invested, shares, total_shares, total_invested):
    return {
        "date": date,
        "price": round(price, 4),
        "invested": invested,
        "shares_bought": round(shares, 6),
        "total_shares": round(total_shares, 6),
        "total_invested": round(total_invested, 2),
        "market_value": round(total_shares * price, 2),
    }
