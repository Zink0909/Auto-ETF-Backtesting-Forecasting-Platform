from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

def forecast_prices_with_prophet(df, periods=30, etf_name="ETF"):
    prophet_df = df[['Date', 'Adj Close']].rename(columns={'Date': 'ds', 'Adj Close': 'y'})
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])

    model = Prophet(daily_seasonality=False)
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    fig = model.plot(forecast)
    plt.title(f"{etf_name} Price Forecast (Prophet)", fontsize=14, weight='bold')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.show()

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], model
