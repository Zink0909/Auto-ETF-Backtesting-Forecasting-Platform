"""Performance and risk metrics -- done correctly.

The legacy code computed CAGR / volatility / Sharpe / Sortino from the **market
value** of the DCA portfolio. That series rises from two unrelated sources --
market moves AND fresh cash contributions -- so every one of those numbers was
contaminated (the "CAGR" even counted your own deposits as investment growth).

This module keeps the two questions separate:

  1. *How did the DCA strategy do, given its cashflows?*  -> money-weighted
     return (XIRR) over the actual contribution stream.
  2. *What are the asset's risk characteristics?*         -> time-weighted
     metrics (vol, Sharpe, Sortino, max drawdown, CAGR) computed on the asset's
     own price returns, NOT on a series polluted by contributions.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq


def xirr(cashflows: list[tuple[pd.Timestamp, float]]) -> float:
    """Money-weighted annualised return for dated cashflows.

    Sign convention: contributions are negative, the final liquidation positive.
    Solves for the rate r where the net present value of all cashflows is zero.
    """
    dates = pd.to_datetime([d for d, _ in cashflows])
    amounts = np.array([a for _, a in cashflows], dtype=float)
    t0 = dates.min()
    years = np.array([(d - t0).days / 365.0 for d in dates])

    def npv(rate: float) -> float:
        return float(np.sum(amounts / (1.0 + rate) ** years))

    if not (amounts.min() < 0 < amounts.max()):
        raise ValueError("cashflows need both signs (contributions and a payout)")
    return brentq(npv, -0.999999, 100.0)


def asset_metrics(prices: pd.Series, risk_free_rate: float = 0.02, trading_days: int = 252) -> dict:
    """Time-weighted risk/return metrics computed on the asset's price series."""
    prices = prices.sort_index().dropna()
    ret = prices.pct_change().dropna()

    years = (prices.index[-1] - prices.index[0]).days / 365.25
    cagr = (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1
    vol = ret.std() * np.sqrt(trading_days)

    downside = ret[ret < 0]
    downside_vol = np.sqrt((downside**2).mean()) * np.sqrt(trading_days) if not downside.empty else 0.0
    drawdown = (prices / prices.cummax() - 1).min()

    return {
        "cagr_pct": round(cagr * 100, 2),
        "volatility_pct": round(vol * 100, 2),
        "sharpe": round((cagr - risk_free_rate) / vol, 2) if vol else 0.0,
        "sortino": round((cagr - risk_free_rate) / downside_vol, 2) if downside_vol else 0.0,
        "max_drawdown_pct": round(drawdown * 100, 2),
        "years": round(years, 2),
    }


def dca_return(cashflows: list[tuple[pd.Timestamp, float]]) -> dict:
    """Money-weighted summary of a DCA cashflow stream."""
    invested = -sum(a for _, a in cashflows if a < 0)
    payout = sum(a for _, a in cashflows if a > 0)
    return {
        "money_weighted_return_pct": round(xirr(cashflows) * 100, 2),
        "total_invested": round(invested, 2),
        "final_value": round(payout, 2),
    }
