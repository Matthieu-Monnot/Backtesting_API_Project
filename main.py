import requests
import pandas as pd
from stats import equal_weighted, Stats

json_data = {
    'code': 'ok',
    'start': '2022-01-01',
    'end': '2023-01-01',
    'assets': ["BTC", "ETH", "BNB"]
}


def fetch_binance_data(asset, start_time, end_time):
    api_url = 'https://api.binance.com/api/v3/klines'
    start = int(start_time.timestamp() * 1000)
    end = int(end_time.timestamp() * 1000)
    all_data = []
    params = {
        'symbol': asset,
        'interval': '1h',
        'limit': 1000
    }
    while start < end:
        params['startTime'] = start
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data)
            start = int(data[-1][0]) + 1
        else:
            print("Erreur lors de la récupération des données:", response.status_code)
            return None
    df = pd.DataFrame(all_data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
                                         'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume',
                                         'Taker Buy Quote Asset Volume', 'ignore'])
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
    df.drop(['ignore'], axis=1, inplace=True)
    df = df[(df['Open Time'] >= start_time) & (df['Open Time'] < end_time)]
    return df


def load_all_data(assets, start, end):
    data = dict()
    for asset in assets:
        data[asset] = fetch_binance_data(asset=f"{asset}USDT", start_time=start, end_time=end)
    return data


if __name__ == "__main__":
    start = pd.Timestamp(json_data["start"])
    end = pd.Timestamp(json_data["end"])
    assets = json_data["assets"]
    dict_data = load_all_data(assets=assets, start=start, end=end)
    print(dict_data["BTC"])

    weights_ts = equal_weighted(dict_data)
    stats = Stats(weights_ts, dict_data)
    stats_json = stats.to_json()
    print(stats_json)
