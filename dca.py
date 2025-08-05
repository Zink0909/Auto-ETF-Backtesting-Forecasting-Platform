import pandas as pd
from datetime import timedelta


def simulate_dca(df, start_date, end_date, invest_amount,
                 frequency='weekly', weekday=0, start_principal=0, 
                 log=False, use_first_trading_day=False):
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except Exception as e:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.") from e

    if start_date >= end_date:
        raise ValueError("start_date must be earlier than end_date.")
    if invest_amount <= 0:
        raise ValueError("invest_amount must be greater than 0.")
    if 'Date' not in df.columns or 'Adj Close' not in df.columns:
        raise ValueError("DataFrame must contain 'Date' and 'Adj Close' columns.")

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].dropna(subset=['Adj Close'])
    trading_dates = df_filtered['Date'].tolist()

    invest_dates, current_date, last_added = [], start_date, None
    while current_date <= end_date:
        if use_first_trading_day and frequency == 'monthly':
            month_data = df_filtered[df_filtered['Date'].dt.to_period("M") == current_date.to_period("M")]
            if not month_data.empty:
                first_day = month_data.iloc[0]['Date']
                if first_day not in invest_dates:
                    invest_dates.append(first_day)
            current_date += pd.offsets.MonthBegin(1)
        else:
            if frequency == 'daily':
                invest_dates.append(current_date)
            elif frequency == 'weekly' and current_date.weekday() == weekday:
                invest_dates.append(current_date)
            elif frequency == 'biweekly' and current_date.weekday() == weekday:
                if not last_added or (current_date - last_added).days >= 14:
                    invest_dates.append(current_date)
                    last_added = current_date
            elif frequency == 'monthly' and current_date.weekday() == weekday:
                if not last_added or current_date.month != last_added.month:
                    invest_dates.append(current_date)
                    last_added = current_date
            current_date += timedelta(days=1)

    actual_invest_dates = [min([d for d in trading_dates if d >= inv], default=None) for inv in invest_dates]
    actual_invest_dates = list(filter(None, actual_invest_dates))

    total_invested, total_shares, log_data = start_principal, 0.0, []
    if start_principal > 0 and actual_invest_dates:
        first_date = actual_invest_dates[0]
        price = df_filtered[df_filtered['Date'] == first_date]['Adj Close'].values[0]
        shares = start_principal / price
        total_shares += shares
        if log:
            log_data.append({
                'Date': first_date, 'Price': round(price, 2), 'Action': 'Initial Investment',
                'Invested': start_principal, 'Shares Bought': round(shares, 4),
                'Total Shares': round(total_shares, 4), 'Total Invested': round(total_invested, 2),
                'Market Value': round(total_shares * price, 2)
            })

    for invest_date in actual_invest_dates:
        row = df_filtered[df_filtered['Date'] == invest_date]
        if not row.empty:
            price = row['Adj Close'].values[0]
            shares = invest_amount / price
            total_shares += shares
            total_invested += invest_amount
            if log:
                log_data.append({
                    'Date': invest_date, 'Price': round(price, 2), 'Action': 'Recurring Investment',
                    'Invested': invest_amount, 'Shares Bought': round(shares, 4),
                    'Total Shares': round(total_shares, 4), 'Total Invested': round(total_invested, 2),
                    'Market Value': round(total_shares * price, 2)
                })

    final_price = df_filtered.iloc[-1]['Adj Close']
    final_value = total_shares * final_price
    total_return = final_value - total_invested
    return_pct = (total_return / total_invested) * 100

    result = {
        'Total Invested': round(total_invested, 2),
        'Total Shares': round(total_shares, 4),
        'Final Price': round(final_price, 2),
        'Final Value': round(final_value, 2),
        'Total Return ($)': round(total_return, 2),
        'Total Return (%)': round(return_pct, 2)
    }

    return (result, pd.DataFrame(log_data)) if log else result
