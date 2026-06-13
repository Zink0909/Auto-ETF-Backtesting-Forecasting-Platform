"""DCA vs lump-sum behaves as theory predicts."""
import numpy as np
import pandas as pd

from etf_dca.benchmark import compare_dca_vs_lump_sum


def test_lump_sum_wins_in_a_rising_market():
    idx = pd.bdate_range("2020-01-01", "2021-12-31")
    prices = pd.Series(np.linspace(100, 200, len(idx)), index=idx)
    cmp = compare_dca_vs_lump_sum(prices, amount=200, frequency="monthly")

    dca = cmp.set_index("strategy").loc["DCA", "total_return_pct"]
    ls = cmp.set_index("strategy").loc["Lump sum", "total_return_pct"]
    # Same capital, steadily rising prices -> being fully invested early wins.
    assert ls > dca
    # Both invested the same amount of capital.
    assert cmp["invested"].nunique() == 1
