import logging
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

from config import config
from dca import simulate_dca
from analysis import analyze_performance
from plotting import plot_single_etf_growth, plot_multi_etf_growth

from prediction import forecast_prices_with_prophet
from export import export_to_excel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def main():
    creds = Credentials.from_service_account_file(config["credential_file"], scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(config["sheet_name"])

    results = []
    log_dict = {}
    forecast_dict = {}

    for etf in config["etf_list"]:
        try:
            df = pd.DataFrame(spreadsheet.worksheet(etf).get_all_records())
            result, log_df = simulate_dca(df, config["start_date"], config["end_date"],
                                          config["invest_amount"], config["frequency"],
                                          config["weekday"], config["start_principal"],
                                          log=config["log"])
            result["ETF"] = etf
            results.append(result)
            log_dict[etf] = log_df
            forecast_df, _ = forecast_prices_with_prophet(df, periods=30, etf_name=etf)
            forecast_dict[etf] = forecast_df
        except Exception as e:
            logging.error(f"ETF {etf} skipped: {e}")

    result_df = pd.DataFrame(results)
    logging.info(f"\nSimulation Summary:\n{result_df}")

    for etf, log_df in log_dict.items():
        metrics = analyze_performance(log_df)
        logging.info(f"\nPerformance Analysis – {etf}:\n{metrics}")
        plot_single_etf_growth(log_df, etf, rolling_window=config["rolling_window"])

    plot_multi_etf_growth(log_dict, rolling_window=config["rolling_window"])
    export_to_excel(result_df, log_dict, forecast_dict)

if __name__ == "__main__":
    main()
