import importlib.util
import json
import sys
import pandas as pd


class Wrapper:
    def __init__(self, file_path: str, function_path: str):
        self.file_path = file_path
        self.function_path = function_path
        self.data_result = None
        self.function_result = None

    def load_data(self):
        with open(self.file_path, "r") as file:
            dico_df_json = json.load(file)
        self.data_result = {key: pd.read_json(df_json) for key, df_json in dico_df_json.items()}
        return self.data_result

    def fonction_run(self):
        self.data_result = self.load_data()
        # Création des spécifications du module à partir du path de la fonction enregistrée en json
        spec = importlib.util.spec_from_file_location("function_module", self.function_path)
        # Création du module à partir des specs
        function_module = importlib.util.module_from_spec(spec)
        # Chargement du module
        spec.loader.exec_module(function_module)
        results = function_module.func_strat(self.data_result)
        self.function_result = results.to_json(orient="index")
        return self.function_result

if __name__=="__main__":
    data_file_path = sys.argv[1]  # Chemin vers le fichier de données JSON.
    user_func_path = sys.argv[2]  # Chemin vers le script de l'utilisateur.
    wrapper = Wrapper(file_path=data_file_path, function_path=user_func_path)
    results = wrapper.fonction_run()
    # Indipensable d'avoir un print pour récuperer le résultat dans le subprocess
    print(results)
