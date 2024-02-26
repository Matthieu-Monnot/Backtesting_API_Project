import json
import numpy as np
import pandas as pd


def calculate_returns_from_dfs(dfs_dict):
    """
    Calcule les rendements des actifs
    :param dfs_dict: dictionnaire de dataframes des prix des actifs
    :return: dataframe contenant les rendements des colonnes 'Close' de chaque dataframe
    """
    df_returns = pd.DataFrame()
    for key, df in dfs_dict.items():
        df_returns[key] = df["Close"].pct_change().fillna(0)
    return df_returns


def Momentum(dfs_dict):
    """
    Calcule la stratégie de rééquilibrage des pondérations en fonction des rendements des actifs.
    :param dfs_dict: Dictionnaire contenant des dataframes de prix.
    :return: DataFrame contenant la série temporelle des poids de chaque actif.
    """
    df_returns = calculate_returns_from_dfs(dfs_dict)
    nb_actifs = len(df_returns.columns)
    pond = {col: 1.0 / nb_actifs for col in df_returns.columns}
    poids_ts = pd.DataFrame(index=df_returns.index, columns=df_returns.columns)
    changement_pond = 0.1
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


def equal_weighted(dfs_dict):
    """
    Calcule la stratégie de rééquilibrage des pondérations en fonction des rendements des actifs.
    :param dfs_dict: Dictionnaire contenant des dataframes de prix.
    :return: DataFrame contenant la série temporelle des poids de chaque actif.
    """
    n = len(dfs_dict)
    t = next(iter(dfs_dict.values())).shape[0]
    col = [1/n for i in range(t)]
    df_weights = pd.DataFrame()
    for key, df in dfs_dict.items():
        df_weights[key + "_weights"] = col
    return df_weights


class Stats:
    def __init__(self, poids_ts, dfs_dict):
        self.poids_ts = poids_ts
        self.dfs_dict = dfs_dict
        self.rf_rate = 0.2
        self.scale = 9
        self.r_indice = self.calculate_index_returns()
        self.setup_metrics()

    def calculate_returns_from_dfs(self):
        df_closes = pd.DataFrame()
        for key, df in self.dfs_dict.items():
            df_closes[key + "_Close"] = df["Close"]
        df_closes = df_closes.astype(float)
        df_returns = df_closes.pct_change().fillna(0)
        return df_returns

    def calculate_index_returns(self):
        df_returns = self.calculate_returns_from_dfs()
        df_index_returns = (df_returns * self.poids_ts).sum(axis=1)
        return df_index_returns.to_frame(name='Index_Return')

    def setup_metrics(self):
        self.r_annual = self.annualize_rets(self.r_indice, self.scale)
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
        'Ratio de Calmar': self.calmar_ratio.item() if isinstance(self.calmar_ratio, pd.Series) else self.calmar_ratio
        }
        return json.dumps(stats_dict, indent=4)
