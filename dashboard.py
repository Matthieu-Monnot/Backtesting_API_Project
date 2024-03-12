import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime


def get_binance_data(start_date, end_date):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime={start_date}&endTime={end_date}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = pd.to_numeric(df['close'])
    return df


def get_color(value):
    if value >= 0:
        return 'rgba(152, 251, 152, 0.7)'  # Vert pastel
    else:
        return 'rgba(255, 182, 193, 0.7)'


def main():
    st.title('Analyse des indicateurs financiers')

    # Sélection des dates de début et de fin
    start_date = st.date_input('Date de début', value=pd.to_datetime('2020-01-01'))
    end_date = st.date_input('Date de fin', value=pd.to_datetime('2021-01-01'))

    if start_date < end_date:
        st.success('Dates sélectionnées valides !')
    else:
        st.error('Erreur : La date de début doit être antérieure à la date de fin.')

    # Affichage des indicateurs
    data_path = os.path.abspath("Data/stats_backtest.json")
    with open(data_path) as json_file:
        data = json.load(json_file)

    # Diviser la page en 2 colonnes
    col1, col2 = st.columns(2)

    # Afficher les informations dans la première colonne
    with col1:
        st.subheader('Performance')
        for key, value in data.items():
            if "Rendement" in key or "Ratio" in key:
                color = get_color(value)
                st.markdown(
                    f'<div style="background-color: {color}; padding: 10px; border-radius: 5px;"><strong>{key}</strong>: {value:.4f}</div>',
                    unsafe_allow_html=True)

    # Afficher les informations dans la deuxième colonne
    with col2:
        st.subheader('Risque')
        for key, value in data.items():
            if "Volatilite" in key or "Deviation" in key or "VaR" in key or "Drawdown" in key or "Skewness" in key or "Kurtosis" in key:
                color = get_color(value)
                st.markdown(
                    f'<div style="background-color: {color}; padding: 10px; border-radius: 5px;"><strong>{key}</strong>: {value:.4f}</div>',
                    unsafe_allow_html=True)

    # Affichage des graphiques si les données sont disponibles
    btc_data = get_binance_data(start_date, end_date)
    btc_data['returns'] = btc_data['close'].pct_change() * 100
    st.line_chart(btc_data['returns'])

    if st.checkbox('Afficher les données brutes'):
        st.write(btc_data)


if __name__ == "__main__":
    main()
