import os
import pandas as pd

def export_to_excel(result_df, log_dict, forecast_dict=None, filename="output/investment_report.xlsx"):
    os.makedirs("output", exist_ok=True)

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        result_df.to_excel(writer, sheet_name="Summary", index=False)

        for etf, df in log_dict.items():
            df.to_excel(writer, sheet_name=f"{etf}_Log", index=False)

        if forecast_dict:
            for etf, forecast_df in forecast_dict.items():
                forecast_df.to_excel(writer, sheet_name=f"{etf}_Forecast", index=False)
