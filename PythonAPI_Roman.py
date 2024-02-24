import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from Data_collector import collect_APIdata


app = FastAPI()
class User_input(BaseModel):
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
        raise HTTPException(status_code=400, detail=f'la récupération des données de calibration de la stratégie à échouée : {str(e)}.')

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
        col = [x +'_close' for x in input.tickers]
        user_data = user_data[col]
        results = user_tradfunc(user_data, float(input.amount))
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de tester la fonction sur données réelles {str(e)}")