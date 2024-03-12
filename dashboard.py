import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timezone
import matplotlib.pyplot as plt


def get_binance_data(start_date, end_date):
    url = "https://data-api.binance.vision/api/v3/klines"
    start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    start_date = int(start_date.timestamp() * 1000)
    end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end_date = int(end_date.timestamp() * 1000)
    params = {
        'symbol': "BTCUSDT",
        'interval': "1d",
        'startTime': start_date,
        'endTime': end_date
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time',
                                     'Quote_volume', 'Nb_trades', 'ignore1', 'ignore2', 'ignore3'])
    df['Dates'] = pd.to_datetime(df['Open_time'], unit='ms')
    df = df[['Close']].set_index(df['Dates'])
    return df


def get_color(value):
    if value >= 0:
        return 'rgba(152, 251, 152, 0.7)'  # Vert pastel
    else:
        return 'rgba(255, 182, 193, 0.7)'


def plot_returns(df):
    # Créer une figure et un axe
    fig, ax = plt.subplots(figsize=(10, 6))

    # Définir les couleurs en fonction des rendements
    colors = ['green' if ret >= 0 else 'red' for ret in df['returns %']]

    # Plot des barres
    ax.bar(df.index, df['returns %'], color=colors)

    # Personnalisation du graphe
    ax.set_title('Rendements en Pourcentage')
    ax.set_xlabel('Date')
    ax.set_ylabel('Rendements %')
    ax.grid(True)

    # Affichage du graphe
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def main():
    st.title('Analyse des indicateurs financiers')

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Date de début', value=pd.to_datetime('2020-01-01'))

    with col2:
        end_date = st.date_input('Date de fin', value=pd.to_datetime('2021-01-01'))


    if start_date < end_date:
        st.success('Dates sélectionnées valides !')
    else:
        st.error('Erreur : La date de début doit être antérieure à la date de fin.')

    # Affichage des indicateurs
    data_path = os.path.abspath("stats_backtest.json")
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

    st.write('\n')

    # Affichage des graphiques si les données sont disponibles
    btc_data = get_binance_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    btc_data = btc_data.astype(float)
    btc_data['returns %'] = btc_data['Close'].pct_change() * 100
    fig = plot_returns(btc_data)
    st.pyplot(fig)

    if st.checkbox('Afficher les données brutes'):
        st.write(btc_data)


if __name__ == "__main__":
    main()
