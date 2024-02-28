import importlib.util
import json
import os.path
import sys
import pandas as pd

def load_data(file_path):
    dataframe = pd.read_json(file_path, orient="index", convert_dates="iso")
    return dataframe
def fonction_run(data, function_path):
    # Création des spécifications du module à partir du path de la fonction enregistrée en json
    spec = importlib.util.spec_from_file_location("function_module", function_path)
    # Création du module à partir des specs
    function_module = importlib.util.module_from_spec(spec)
    # Chargement du module
    spec.loader.exec_module(function_module)

    results = function_module.func_strat(data)
    results_json = results.to_json(orient="index")
    return results_json

if __name__=="__main__":
    data_file_path = sys.argv[1]  # Chemin vers le fichier de données JSON.
    user_func_path = sys.argv[2]  # Chemin vers le script de l'utilisateur.
    # data_file_path = os.path.abspath("user_data.json")
    # user_func_path = os.path.abspath("user_function.py")
    data_df = load_data(data_file_path)
    results = fonction_run(data_df, user_func_path)
    # Indipensable d'avoir un print pour récuperer le résultat dans le subprocess
    print(results)
