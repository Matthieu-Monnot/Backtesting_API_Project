
import pandas
#
# def func_strat(df_dict, amount=1000):
#     df_returns = pandas.DataFrame()
#     for key, df in df_dict.items():
#         df_returns[key] = df["Close"]
#     nb_assets = len(df_returns.columns)
#     w = 1.0/nb_assets
#     weights = {col: [w]*len(df_returns) for col in df_returns.columns}
#     positions = pandas.DataFrame(weights)
#     return positions

def func_strat(dfs_dict):
    df_returns = pandas.DataFrame()
    for key, df in dfs_dict.items():
        df_returns[key] = df["Close"]
    df_returns = df_returns.pct_change().fillna(0)
    nb_actifs = len(df_returns.columns)
    pond = {col: 1.0 / nb_actifs for col in df_returns.columns}
    poids_ts = pandas.DataFrame(index=df_returns.index, columns=df_returns.columns)

    changement_pond = 0.1

    for i, date in enumerate(df_returns.index):

        if i % 2 == 0 and i > 0:
            total_pond = 0
            for col in df_returns.columns:
                rendement_2_jours = df_returns[col].iloc[i] - df_returns[col].iloc[i - 2]
                if rendement_2_jours > 0:
                    pond[col] = min(pond[col] + changement_pond, 1)
                else:
                    pond[col] = max(pond[col] - changement_pond, 0)
                total_pond += pond[col]

            for col in pond:
                pond[col] /= total_pond

        for col in df_returns.columns:
            poids_ts.at[date, col] = pond[col]

    return poids_ts

if __name__=='__main__':
    dfs_dict = {
        "df1": pandas.DataFrame({
            "Close": [1, 2, 3],
            "Open": [4, 5, 6]
        }),
        "df2": pandas.DataFrame({
            "Close": [0.1, 0.2, 0.3],
            "Open": [0.4, 0.5, 0.6]
        })
    }
    positions = func_strat(dfs_dict)
    print(positions)