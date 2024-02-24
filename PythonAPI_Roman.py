import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from Data_collector import collect_APIdata
import numpy as np
from fastapi.responses import JSONResponse


app = FastAPI()
class User_input(BaseModel):
    """
    Modèle de requête suivi par l'utilisateur :
    func_strat : La fonction de trading de l'utilisateur en str qui renvoie un poids dans pour chaque actifs à chaque
    date dans le portefeuille
    requirements : liste des imports
    tickers : liste des tickers considérés
    dates_calibrations : liste des dates pour calibrer la fonction de stratégie
    dates_test : dates sur lesquels ont teste la stratégie de trading
    interval : fréquence des observations considérées
    amount : montant du portefeuille
    """
    func_strat: str
    requirements: list[str]
    tickers: list[str]
    dates_calibration: list[str]
    dates_test : list[str]
    interval: str
    amount: str

# Création de la route
@app.post('/backtesting/')
async def backtest(input: User_input):
    try:
        user_data = collect_APIdata(input.tickers, input.dates_calibration, input.interval)
        if not isinstance(user_data, pd.DataFrame):
            return print("pas un df pandas")
        else:
            pass
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'la récupération des données de calibration de la \n'
                                                    f'stratégie à échouée : {str(e)}.')
    context = {}
    for requirement in input.requirements:
        exec(requirement, {}, context)

    try:
        exec(input.func_strat, context, context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Impossible de run la fonction de trading : {str(e)}')

    user_tradfunc = context.get("trading_strat")
    if not user_tradfunc:
        raise HTTPException(status_code=400, detail="La fonction n'as pas été définie correctement")

    try:
        col = [x + '_close' for x in input.tickers]
        user_data = user_data[col]
        results = user_tradfunc(user_data, float(input.amount))
        results.columns = user_data.columns
        portfolio = results.astype(float).multiply(user_data.astype(float), axis="index")
        portfolio = portfolio.to_dict(orient="records")
        if not isinstance(results, pd.DataFrame):
            raise ValueError('pas df pd')
        else:
            return JSONResponse(content=portfolio)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de tester la fonction sur données réelles : {str(e)}")
