"""Performance metrics: XIRR and asset risk metrics."""
import numpy as np
import pandas as pd

from etf_dca.performance import xirr, asset_metrics


def test_xirr_recovers_known_rate():
    cf = [(pd.Timestamp("2021-01-01"), -1000.0), (pd.Timestamp("2022-01-01"), 1100.0)]
    assert abs(xirr(cf) - 0.10) < 1e-3


def test_xirr_requires_sign_change():
    import pytest

    with pytest.raises(ValueError):
        xirr([(pd.Timestamp("2021-01-01"), -100.0), (pd.Timestamp("2022-01-01"), -50.0)])


def test_asset_metrics_flat_price_is_zero_risk():
    idx = pd.bdate_range("2020-01-01", "2021-01-01")
    m = asset_metrics(pd.Series(100.0, index=idx))
    assert m["cagr_pct"] == 0.0
    assert m["volatility_pct"] == 0.0
    assert m["max_drawdown_pct"] == 0.0


def test_asset_metrics_rising_price_positive_cagr():
    idx = pd.bdate_range("2020-01-01", "2021-12-31")
    prices = pd.Series(np.linspace(100, 150, len(idx)), index=idx)
    m = asset_metrics(prices)
    assert m["cagr_pct"] > 0
    assert m["max_drawdown_pct"] == 0.0   # monotonic, no drawdown
