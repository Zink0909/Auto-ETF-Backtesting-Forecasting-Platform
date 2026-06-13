"""DCA engine: accounting identities and contribution scheduling."""
import pandas as pd

from etf_dca.dca import simulate_dca, contribution_dates


def _constant_prices(price=100.0):
    idx = pd.bdate_range("2020-01-01", "2020-12-31")
    return pd.Series(price, index=idx)


def test_constant_price_means_zero_return():
    res = simulate_dca(_constant_prices(100.0), amount=200, frequency="monthly")
    # 12 monthly buys of $200 each.
    assert res.summary["total_invested"] == 2400
    # With a flat price, market value equals money in -> zero profit.
    assert abs(res.summary["total_return_pct"]) < 1e-6
    assert abs(res.summary["final_value"] - 2400) < 1e-6


def test_shares_accumulate_correctly():
    res = simulate_dca(_constant_prices(50.0), amount=100, frequency="monthly")
    # Each $100 buys 2 shares at price 50; 12 months -> 24 shares.
    assert abs(res.summary["total_shares"] - 24) < 1e-6


def test_monthly_schedule_has_twelve_dates():
    idx = pd.bdate_range("2020-01-01", "2020-12-31")
    assert len(contribution_dates(idx, "monthly")) == 12


def test_start_principal_is_invested():
    res = simulate_dca(_constant_prices(100.0), amount=200, frequency="monthly",
                       start_principal=1000)
    assert res.summary["total_invested"] == 2400 + 1000
