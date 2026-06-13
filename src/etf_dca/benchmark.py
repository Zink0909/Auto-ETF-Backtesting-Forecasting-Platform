"""DCA vs. lump-sum -- the classic question.

Given the *same* total capital, is it better to drip it in over time (DCA) or
invest it all on day one (lump sum)? Lump sum tends to win in rising markets
(more time in market) while DCA reduces timing risk. We compare both on equal
capital so the answer is apples-to-apples.
"""
from __future__ import annotations

import pandas as pd

from .dca import simulate_dca


def compare_dca_vs_lump_sum(
    prices: pd.Series,
    amount: float,
    frequency: str = "monthly",
    weekday: int = 0,
    start_principal: float = 0.0,
) -> pd.DataFrame:
    prices = prices.sort_index()
    dca = simulate_dca(prices, amount, frequency, weekday, start_principal)

    # Lump sum: deploy the same total capital at the first trading day.
    capital = dca.summary["total_invested"]
    p0 = float(prices.iloc[0])
    final_price = float(prices.iloc[-1])
    ls_value = capital / p0 * final_price

    rows = [
        {
            "strategy": "DCA",
            "invested": capital,
            "final_value": dca.summary["final_value"],
            "total_return_pct": dca.summary["total_return_pct"],
        },
        {
            "strategy": "Lump sum",
            "invested": round(capital, 2),
            "final_value": round(ls_value, 2),
            "total_return_pct": round((ls_value / capital - 1) * 100, 2),
        },
    ]
    return pd.DataFrame(rows)
