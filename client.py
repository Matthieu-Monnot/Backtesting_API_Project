import pandas as pd
import requests
import json

url = "http://127.0.0.1:8000/backtesting/"

fonction_trading = """
import pandas as pd

def trading_strat(data, amount):
    nb_assets = len(data.columns)
    w = 1.0/nb_assets
    pos = pd.DataFrame(index=data.index)
    for col in data.columns:
        pos[col + '_pos'] = amount*w
    return pos
"""

params = {
    "func_strat": fonction_trading,
    "requirements": ["import pandas as pd"],
    "tickers": ["ETHBTC", "BNBETH"],
    "dates_calibration": ["2023-01-01", "2023-01-15"],
    "dates_test" : ["2023-01-01", "2024-01-01"],
    "interval": "1d",
    "amount": "10000"
}

response = requests.post(url, json=params)
print(response.json())
