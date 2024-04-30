import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from requests import post
import time


URL = "https://backtestapi.onrender.com/backtesting/"


# Couleurs personnalisées
background_color = "#f0f0f0"
button_color = "#4CAF50"
button_hover_color = "#45a049"
text_color = "black"
border_color = "black"

# Configuration du style Streamlit
st.markdown(
    f"""
    <style>
    body {{
        color: {text_color};
        background-color: {background_color};
    }}
    .stButton>button {{
        background-color: {button_color};
        color: white;
        font-weight: bold;
        border-color: {border_color};
        border-width: 2px;
        border-style: solid;
    }}
    .stButton>button:hover {{
        background-color: {button_hover_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_color(value):
    if value >= 0:
        return 'rgba(152, 251, 152, 0.7)'  # Vert pastel
    else:
        return 'rgba(255, 182, 193, 0.7)'


def show_homepage():
    st.title("Modélisation et Pricing de produits structurés")
    st.markdown("""
    **Objectif :** Le but de ce projet est de développer une API permettant aux utilisateurs de soumettre leurs propres stratégies de trading algorithmique pour backtesting. Le système doit être capable d’exécuter ces stratégies sur des données de marché historiques et de fournir des analyses de performance sur la période spécifiée.
    """)


def show_backtesting():
    st.title('Backtesting de stratégie de trading')

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Date de début', max_value=datetime.today() + timedelta(days=365 * 100), format="DD-MM-YYYY")

    with col2:
        end_date = st.date_input('Date de fin', max_value=datetime.today() + timedelta(days=365 * 100), format="DD-MM-YYYY")

    if start_date < end_date:
        st.success('Dates sélectionnées valides !')
    else:
        st.error('Erreur : La date de début doit être antérieure à la date de fin.')

    func_strat = st.text_input("Fonction de trading avec les imports", value="import pandas as pd \n def fonction_trading(df: pd.DataFrame):\n ... \n df_positions = pd.DataFrame() \n return df_positions")
    requirements = st.text_input("Imports nécessaires à la stratégie", value=["pandas", "numpy"])
    tickers = st.text_input("Actifs utilisés dans la stratégie", value=["ETHBTC", "BNBETH"])
    interval = st.text_input("Fréquence des données de marché", value="1d")
    request_id = st.text_input("Id de la requête. Doit être unique !", value="12345")
    is_recurring = st.selectbox("Répéter le backtest ?", [True, False])

    if is_recurring:
        repeat_frequency = st.number_input("fréquence de répétition", value=2)
    else:
        repeat_frequency = 0

    if st.button("Backtest"):
        with st.spinner("Calculating..."):
            data = {
                "func_strat": func_strat,
                "requirements": requirements,
                "tickers": tickers,
                "dates": [start_date, end_date],
                "interval": interval,
                "amount": "10000",
                "request_id": request_id,
                "is_recurring": is_recurring,
                "repeat_frequency": repeat_frequency,
                "nb_execution": 1
            }

            res = post(url=URL, data=json.dumps(data)).json()
            st.success("Backtest réussi !")


    col1, col2 = st.columns(2)

    # Afficher les informations dans la première colonne
    with col1:
        st.subheader('Performance')
        for key, value in res.items():
            if "Rendement" in key or "Ratio" in key:
                color = get_color(value)
                st.markdown(
                    f'<div style="background-color: {color}; padding: 10px; border-radius: 5px;"><strong>{key}</strong>: {value:.4f}</div>',
                    unsafe_allow_html=True)

    # Afficher les informations dans la deuxième colonne
    with col2:
        st.subheader('Risque')
        for key, value in res.items():
            if "Volatilite" in key or "Deviation" in key or "VaR" in key or "Drawdown" in key or "Skewness" in key or "Kurtosis" in key:
                color = get_color(value)
                st.markdown(
                    f'<div style="background-color: {color}; padding: 10px; border-radius: 5px;"><strong>{key}</strong>: {value:.4f}</div>',
                    unsafe_allow_html=True)


def main():
    pages = {
        "Page d'accueil": show_homepage,
        "Backtest de stratégies": show_backtesting,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    page = pages[selection]
    page()


if __name__ == "__main__":
    main()
