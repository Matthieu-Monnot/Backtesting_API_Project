import requests
import subprocess
import platform
import pandas as pd


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


def create_venv(name, packages):
    try:
        subprocess.run(["python", "-m", "venv", name], check=True)
    except subprocess.CalledProcessError:
        return f"Erreur lors de la création de l'environnement virtuel {name}"

    system = platform.system()
    activate_cmd = f"{name}/Scripts/activate" if system == 'Windows' else f"{name}/bin/activate"
    subprocess.run([activate_cmd], shell=True)

    packages_not_installed = []
    for package in packages:
        try:
            subprocess.run(["pip", "install", package], check=True)
        except subprocess.CalledProcessError:
            packages_not_installed.append(package)

    subprocess.run(["deactivate"], shell=True)

    if packages_not_installed:
        return f"Les packages suivants n'ont pas pu être installés : {', '.join(packages_not_installed)}"
    else:
        return f"Tous les packages ont été installés avec succès dans l'environnement virtuel {name}"


if __name__ == "__main__":
    """
    start = pd.Timestamp(json_data["start"])
    end = pd.Timestamp(json_data["end"])
    assets = json_data["assets"]
    dict_data = load_all_data(assets=assets, start=start, end=end)
    print(dict_data["BTC"])
    """
    packages_to_install = ["numpy", "pandas","zblurb", "matplotlib"]
    result_message = create_venv("mon_env", packages_to_install)
    print(result_message)

