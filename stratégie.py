import asyncio
import aiohttp
import pandas as pd
import numpy as np
import json
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import matplotlib.pyplot as plt

async def fetch_market_data(session, id_categorie):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={id_categorie}&per_page=250&sparkline=false&locale=en"
    try:
        async with session.get(url) as response:
            data_per_cate = await response.json()
            # Récupération de l'ID et de la capitalisation boursière de chaque crypto
            return [{'id': crypto['id'], 'market_cap': crypto['market_cap']} for crypto in data_per_cate]
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour la catégorie {id_categorie}: {e}")
        return []

async def get_data(parametres_backtest):
    async with aiohttp.ClientSession() as session:
        tags = parametres_backtest["tags"]
        ids_categories = []
        crypto_data = []

        # Récupération des IDs de catégorie
        async with session.get("https://api.coingecko.com/api/v3/coins/categories") as response:
            categories_data = await response.json()

        for categorie in categories_data:
            contenu_categorie = " ".join(str(valeur) for valeur in categorie.values())
            for tag in tags:
                if tag.lower() in contenu_categorie.lower():
                    ids_categories.append(categorie['id'])
                    break
        print(f'la liste ids par catégorie est la suivante {ids_categories}')

        tasks = [fetch_market_data(session, id_categorie) for id_categorie in ids_categories]
        results = await asyncio.gather(*[asyncio.wait_for(task, timeout=15) for task in tasks])

        for data in results:
            crypto_data.extend(data)

        data_frame = pd.DataFrame(crypto_data)
        return data_frame

        # Part Cyprien ----------------------------------------------------------------------------------------------

def calculate_returns_from_dfs(dfs_dict):
    """
    Prend en entrée un dictionnaire de dataframes et retourne une dataframe
    contenant les rendements des colonnes 'Close' de chaque dataframe.
    """
    # Initialiser une dataframe vide pour les prix de clôture
    df_closes = pd.DataFrame()

    for key, df in dfs_dict.items():
        df_closes[key + "_Close"] = df["Close"]
    
    # Initialiser une dataframe pour les rendements
    df_returns = pd.DataFrame()
    
    # Calculer les rendements pour chaque colonne de prix de clôture
    for col in df_closes.columns:
        df_returns[col] = df_closes[col].pct_change().fillna(0) # + "_Return"
    
    return df_returns

def Momentum(dfs_dict):
    """
    Calcule la stratégie de rééquilibrage des pondérations en fonction des rendements des actifs.
    
    Args:
    dfs_dict (dict): Dictionnaire contenant des dataframes de prix.
    
    Returns:
    pd.DataFrame: DataFrame contenant la série temporelle des poids de chaque actif.
    """
    # Aggréger les prix dans une seule dataframe et calculer les rendements
    df_returns = calculate_returns_from_dfs(dfs_dict)
    
    nb_actifs = len(df_returns.columns)
    pond = {col: 1.0 / nb_actifs for col in df_returns.columns}
    poids_ts = pd.DataFrame(index=df_returns.index, columns=df_returns.columns)
    
    changement_pond=0.1

    for i, date in enumerate(df_returns.index):
        # Mise à jour des pondérations tous les 2 jours
        if i % 2 == 0 and i > 0:
            total_pond = 0
            for col in df_returns.columns:
                rendement_2_jours = df_returns[col].iloc[i] - df_returns[col].iloc[i - 2]
                if rendement_2_jours > 0:
                    pond[col] = min(pond[col] + changement_pond, 1)
                else:
                    pond[col] = max(pond[col] - changement_pond, 0)
                total_pond += pond[col]

            # Normaliser les pondérations pour qu'elles somment à 1
            for col in pond:
                pond[col] /= total_pond
        
        # Enregistrer les pondérations pour la date courante
        for col in df_returns.columns:
            poids_ts.at[date, col] = pond[col]
    
    return poids_ts

class Stats:
    def __init__(self, poids_ts, dfs_dict, user_input):
        self.poids_ts = poids_ts
        self.dfs_dict = dfs_dict
        self.rf_rate = user_input['riskfree_rate']
        self.scale = user_input['scale']
        self.r_indice = self.calculate_index_returns()
        self.setup_metrics()

    def calculate_returns_from_dfs(self):
        df_closes = pd.DataFrame()
        for key, df in self.dfs_dict.items():
            df_closes[key + "_Close"] = df["Close"]
        df_returns = df_closes.pct_change().fillna(0)
        return df_returns

    def calculate_index_returns(self):
        df_returns = self.calculate_returns_from_dfs()
        df_index_returns = (df_returns * self.poids_ts).sum(axis=1)
        return df_index_returns.to_frame(name='Index_Return')

    def setup_metrics(self):
        self.r_annual = self.annualize_rets(self.r_indice,self.scale)
        self.vol_annual = self.annualize_vol()
        self.sharpe_r = self.sharpe_ratio()
        self.skew = self.skewness()
        self.kurt = self.kurtosis()
        self.semi_deviation = self.semideviation()
        self.var_hist = self.var_historic()
        self.max_draw = self.compute_drawdowns()
        self.downside_vol = self.downside_volatility()
        self.sortino_ratio = self.sortino_ratio()
        self.calmar_ratio = self.calmar_ratio()
    

    @staticmethod
    def annualize_rets(r, scale):
        compounded_growth = (1 + r).prod()
        n_periods = r.shape[0]
        return compounded_growth ** (scale / n_periods) - 1

    def annualize_vol(self):
        return self.r_indice.std() * np.sqrt(self.scale)

    def sharpe_ratio(self):
        rf_per_period = (1 + self.rf_rate) ** (1 / self.scale) - 1
        excess_ret = self.r_indice - rf_per_period
        return self.annualize_rets(excess_ret,self.scale) / self.annualize_vol()

    def skewness(self):
        demeaned_r = self.r_indice - self.r_indice.mean()
        return (demeaned_r ** 3).mean() / (self.r_indice.std(ddof=0) ** 3)

    def kurtosis(self):
        demeaned_r = self.r_indice - self.r_indice.mean()
        return (demeaned_r ** 4).mean() / (self.r_indice.std(ddof=0) ** 4)

    def semideviation(self):
        return self.r_indice[self.r_indice < 0].std(ddof=0)

    def var_historic(self, level=5):
        return np.percentile(self.r_indice, level)

    def compute_drawdowns(self):
        peaks = self.r_indice.cummax()
        drawdowns = (self.r_indice - peaks) / peaks
        return drawdowns.min()

    def downside_volatility(self):
        downside = np.minimum(self.r_indice - self.rf_rate, 0)
        return np.sqrt(np.mean(downside ** 2))

    def sortino_ratio(self):
        rf_per_period = (1 + self.rf_rate) ** (1 / self.scale) - 1
        excess_return = self.r_indice - rf_per_period
        return self.annualize_rets(excess_return,self.scale) / self.downside_volatility()

    def calmar_ratio(self):
        return self.r_annual / -self.max_draw

    
    def to_json(self):
        # Collecter les statistiques dans un dictionnaire
        stats_dict = {
        'Rendement Annuel': self.r_annual.item() if isinstance(self.r_annual, pd.Series) else self.r_annual,
        'Volatilite Annuelle': self.vol_annual.item() if isinstance(self.vol_annual, pd.Series) else self.vol_annual,
        'Ratio de Sharpe': self.sharpe_r.item() if isinstance(self.sharpe_r, pd.Series) else self.sharpe_r,
        'Skewness': self.skew.item() if isinstance(self.skew, pd.Series) else self.skew,
        'Kurtosis': self.kurt.item() if isinstance(self.kurt, pd.Series) else self.kurt,
        'Semi-Deviation': self.semi_deviation.item() if isinstance(self.semi_deviation, pd.Series) else self.semi_deviation,
        'VaR Historique': self.var_hist.item() if isinstance(self.var_hist, pd.Series) else self.var_hist,
        'Drawdown Maximal': self.max_draw.item() if isinstance(self.max_draw, pd.Series) else self.max_draw,
        'Volatilite a la Baisse': self.downside_vol.item() if isinstance(self.downside_vol, pd.Series) else self.downside_vol,
        'Ratio de Sortino': self.sortino_ratio.item() if isinstance(self.sortino_ratio, pd.Series) else self.sortino_ratio,
        'Ratio de Calmar': self.calmar_ratio.item() if isinstance(self.calmar_ratio, pd.Series) else self.calmar_ratio,
    }
        return json.dumps(stats_dict, indent=4)
    


if __name__ == '__main__':
    #parametres_backtest = {
    #    "tags": ["DeFi", "blockchain"]
    #}
    #data_frame = asyncio.run(get_data(parametres_backtest))
    #print(data_frame)

    # Part Cyprien ----------------------------------------------------------------------------------------------
    col_names = [
    "Open Time", "Open", "High", "Low", "Close", "Volume",
    "Close Time", "Quote Asset Volume", "Number of Trades",
    "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume"
    ]
    
    # Créer deux dataframes fictives qu'il faudra supprimer
    def generate_market_data(num_rows):
        df = pd.DataFrame(columns=col_names)
        # Générer des prix d'ouverture
        df['Open'] = np.random.normal(loc=100, scale=10, size=num_rows).clip(min=1)
        # Assurer que 'Close' est proche de 'Open', 'High' est le maximum, 'Low' est le minimum
        df['Close'] = df['Open'] + np.random.normal(loc=0, scale=2, size=num_rows)
        df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.uniform(1, 5, size=num_rows)
        df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.uniform(1, 5, size=num_rows)
        # Assurer que 'Low' est inférieur à 'Open' et 'Close', et 'High' est supérieur
        df['Low'] = df[['Low', 'Open', 'Close']].min(axis=1)
        df['High'] = df[['High', 'Open', 'Close']].max(axis=1)
        # Les autres colonnes peuvent être générées avec des valeurs aléatoires ou fixes
        df['Volume'] = np.random.uniform(1000, 10000, size=num_rows)
        df['Quote Asset Volume'] = df['Volume'] * df['Close']
        df['Number of Trades'] = np.random.randint(100, 1000, size=num_rows)
        df['Taker Buy Base Asset Volume'] = df['Volume'] * np.random.uniform(0.5, 1.0, size=num_rows)
        df['Taker Buy Quote Asset Volume'] = df['Taker Buy Base Asset Volume'] * df['Close']
        # Pour 'Open Time' et 'Close Time', on peut simuler des timestamps
        df['Open Time'] = pd.date_range(start='2022-01-01', periods=num_rows, freq='D')
        df['Close Time'] = df['Open Time'] + pd.Timedelta(hours=24)
        
        return df

    df1 = generate_market_data(10)
    df2 = generate_market_data(10)
    print(df1)
    
    dict_of_dfs = {"DataFrame1": df1, "DataFrame2": df2}

    # Créer dico users
    dic_user = {
        'categories': "selected_categories",
        'selected_cryptos': "selected_symbols",
        'selected_ids': "selected_ids",
        'startTime': '2022-04-01',
        'endTime': '2023-04-07',
        'frequency': '1d',
        'strategies': 'Momentum', # 'Equipondere','MoyenneMobile'
        'riskfree_rate': 0.2,
        'scale': 9
    }

    poids_ts = Momentum(dict_of_dfs)
    print(poids_ts)
    stats = Stats(poids_ts, dict_of_dfs, dic_user)
    stats_json = stats.to_json()

    print(stats_json)




