import matplotlib.pyplot as plt


def plot_single_etf_growth(log_df, etf_name, rolling_window=None):
    df = log_df.copy()
    df['Profit (%)'] = (df['Market Value'] / df['Total Invested'] - 1) * 100
    if rolling_window and rolling_window > 1:
        df['Smoothed'] = df['Profit (%)'].rolling(rolling_window, min_periods=1).mean()
        y = df['Smoothed']
        label = f"{etf_name} (Rolling {rolling_window})"
    else:
        y = df['Profit (%)']
        label = etf_name

    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], y, marker='o', label=label)
    plt.title(f"Profit % Over Time – {etf_name}")
    plt.xlabel("Date")
    plt.ylabel("Profit (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_multi_etf_growth(log_dict, rolling_window=None, show_volatility=False):
    plt.figure(figsize=(12, 6))
    for etf, df in log_dict.items():
        df = df.copy()
        df['Profit (%)'] = (df['Market Value'] / df['Total Invested'] - 1) * 100
        if rolling_window and rolling_window > 1:
            df['Smoothed'] = df['Profit (%)'].rolling(rolling_window, min_periods=1).mean()
            plt.plot(df['Date'], df['Smoothed'], label=f"{etf} (Rolling {rolling_window})", marker='o')
        else:
            plt.plot(df['Date'], df['Profit (%)'], label=etf, marker='o')

        if show_volatility and rolling_window:
            df['Vol'] = df['Profit (%)'].rolling(rolling_window, min_periods=1).std()
            upper = df['Smoothed'] + df['Vol']
            lower = df['Smoothed'] - df['Vol']
            plt.fill_between(df['Date'], lower, upper, alpha=0.2)

    plt.title("Multi-ETF Profit Comparison")
    plt.xlabel("Date")
    plt.ylabel("Profit (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
