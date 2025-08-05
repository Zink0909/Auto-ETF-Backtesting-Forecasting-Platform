config = {
    "etf_list": ["SPY", "QQQ", "VTI"],
    "start_date": "2022-01-01",
    "end_date": "2024-12-31",
    "invest_amount": 200,
    "frequency": "monthly",
    "weekday": 0,
    "start_principal": 1000,
    "log": True,
    "rolling_window": 5,
    "sheet_name": "ETF Tracker",
    "credential_file": "etf-data-access-435896d96122.json"
}

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
