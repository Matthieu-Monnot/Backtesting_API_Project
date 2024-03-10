# Backtesting API Project

API pour Backtesting de Stratégies de Trading Algorithmique.


## Objectif du Projet
Le but de ce projet est de développer une API permettant aux utilisateurs de soumettre leurs propres stratégies de trading algorithmique pour backtesting. Le système doit être capable d’exécuter ces stratégies sur des données de marché historiques et de fournir des analyses de performance sur la période spécifiée.


## Fonctionnalités Clés

### 1. Soumission de Fonctions de Trading :
• L'utilisateur soumet une stratégie de trading que notre système va évaluer par backtesting sur des données de marché historiques. La fonction de trading prend la forme d'un script python et de plusieurs inputs afin de mesurer la performance de la stratégie.

• Le système contrôle les fonctions soumises pour garantir leur exécution sûre et conforme lors du backtesting.

### 2. Backtesting :
• L'analyse de la performance par backtesting est réalisé à partir de données de marché historiques des actifs de l'univers d'investissement. Nous utilisons les barres de prix OHLCV afin de calculer les différents indicateurs demandés par l'utilisateur.

• La réponse de l'API fournit des statistiques et des analyses de performance pour la stratégie testée.

### 3. Stockage et Exécution Programmée :
• L'API permet également de planifier des backtests à des intervalles spécifiés par l’utilisateur avec la même stratégie de trading. Ceci permet d'éviter de requêter plusieurs fois l'API avec la même fonction de trading.


## Utilisation

Les fonctionnalités de backtesting de stratégie de trading algorithmique sont utilisable directement via une requête POST à l'API développée. Cette API prend en entrée plusieurs paramètres afin de renvoyer les indicateurs de performances souhaités à l'utilisateur.

Les paramètres d'entrée de l'API sont collectés par un dictionnaire json puis inséré dans la requête de l'API comme suit :

```python
params = {"code": "fonction_de_trading", "indicateurs": ["sharp_ratio"], "start": "01-01-2022", "end": "31-12-2022", "actifs": ["AAPL", "GOOGL"], "packages": ["numpy"], "reuse": False, "interval": 0}
response = requests.post(url, data=params)
```

Les arguments pris en compte sont les suivants :
- code : script python qui applique la stratégie de trading. La stratégie de trading doit prendre en entrée des données historiques d'actifs et renvoyer la position sur la prochaine période. Les données historiques peuvent être consultées en appelant une fonction externe "load_data(asset, start, end)" et qui renvoie un dataframe avec une ligne par jour de trading et les variables suivantes :
    - Open Time (t) : L’heure de début du chandelier.
    - Open (o) : Le prix d'ouverture du chandelier.
    - High (h) : Le prix le plus élevé pendant la période du chandelier.
    - Low (l) : Le prix le plus bas pendant la période du chandelier.
    - Close (c) : Le prix de clôture du chandelier.
    - Volume (v) : Le volume total des actifs de base pendant la période du chandelier.
    - Close Time (T) : L’heure de fermeture du chandelier.
    - Quote Asset Volume (q) : Le volume total des actifs de cotation pendant la période du chandelier.
    - Number of Trades (n) : nombre de transactions effectuées pendant la période du chandelier.
    - Taker Buy Base Asset Volume (V) : volume total d'actifs de base attribué aux achats des taker au cours de la période du chandelier.
    - Taker Buy Quote Asset Volume (Q) : volume total d'actifs de cotation attribué aux achats des taker au cours de la période du chandelier.
- indicateurs : liste d'indicateurs parmis les suivants : return (rendement moyen), vol (volatilité du portefeuille), sharp_ratio (ratio de sharp de l'investissement) et beta (sensibilité de la valeur de l'actif aux variations du marché)
- start : début de la période de backtesting au format "dd-mm-aaaa"
- end : fin de la période de backtesting au format "dd-mm-aaaa"
- actifs (univers d'investissement) : actifs à tester parmis la liste suivante : "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "TSLA", "META", "GOOG", "BRK.B" et "UNH"
- packages : liste de packages (pip) requis pour exécuter la fonction de trading dans un environnement virtuel possédant uniquement python 3.10
- reuse : True ou False pour indiquer si l'utilisateur veut planifier d'autres backtests dans le futur
- interval : int, nombre de mois d'intervalle entre chaque backtest à partir de la date de requête

### Exemple d'utilisation

```python 
import requests

# URL de l'API
url = "https://exemple.com/api/endpoint"

# Code Python que vous souhaitez envoyer
script_code = """
print("Hello, world!")
"""

# Paramètres de la requête POST
payload = {
    'code': script_code
}

# Envoi de la requête POST
response = requests.post(url, data=payload)

# Lecture de la réponse JSON
json_data = response.json()
```


Le test de l'API de backtest est live sur https://backtestapi.onrender.com/backtesting/.
Elle peut être testée avec la requête exemple dans le fichier client.py
