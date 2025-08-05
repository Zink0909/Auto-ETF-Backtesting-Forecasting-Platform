import numpy as np


def analyze_performance(log_df, risk_free_rate=0.02):
    df = log_df.copy().sort_values('Date')
    df['Log Return'] = np.log(df['Market Value'] / df['Market Value'].shift(1))
    df.dropna(inplace=True)

    start_value, end_value = df['Market Value'].iloc[0], df['Market Value'].iloc[-1]
    years = (df['Date'].iloc[-1] - df['Date'].iloc[0]).days / 365.25
    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
    volatility = df['Log Return'].std() * np.sqrt(252) * 100

    cumulative = np.exp(df['Log Return'].cumsum())
    peak = cumulative.cummax()
    max_drawdown = ((cumulative - peak) / peak).min() * 100

    sharpe = (cagr - risk_free_rate * 100) / volatility if volatility else 0
    downside = df['Log Return'][df['Log Return'] < 0]
    downside_std = np.sqrt(np.mean(downside ** 2)) * np.sqrt(252) * 100 if not downside.empty else 0
    sortino = (cagr - risk_free_rate * 100) / downside_std if downside_std else 0

    return {
        'CAGR (%)': round(cagr, 2),
        'Volatility (%)': round(volatility, 2),
        'Max Drawdown (%)': round(max_drawdown, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Sortino Ratio': round(sortino, 2),
        'Years Invested': round(years, 2)
    }
