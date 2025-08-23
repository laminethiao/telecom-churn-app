# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import os

# Définition du modèle de données d'entrée
class Item(BaseModel):
    Age: float
    Gender: str
    Country: str
    Education_Level: str
    Profession: str
    Annual_Salary: float
    Experience_Years: float
    Spending_Score: float
    Family_Size: float

# Initialisation de l'application FastAPI
app = FastAPI()

# Chargement du modèle et des colonnes de l'encodeur
# Les chemins d'accès sont ajustés pour correspondre à la structure de votre projet.
try:
    # Charger le modèle joblib depuis le dossier 'model'
    model = joblib.load('model/modele_random_forest.pkl')

    # Charger les noms de colonnes de l'encodeur depuis le dossier 'model'
    feature_columns = joblib.load('model/training_columns.pkl')
except FileNotFoundError as e:
    print(f"Erreur: Fichier introuvable. Assurez-vous que les fichiers '.pkl' sont bien dans le sous-dossier 'model'. Détails: {e}")
    # En cas d'échec du chargement, le programme ne peut pas continuer.
    model = None
    feature_columns = None

# Définition de l'endpoint pour la prédiction
@app.post("/predict")
def predict(item: Item):
    if model is None or feature_columns is None:
        return {"error": "Modèle ou colonnes non chargés. Veuillez vérifier la présence des fichiers."}

    # Création d'un DataFrame à partir des données de l'utilisateur
    input_data = pd.DataFrame([item.dict()])

    # Ajout des colonnes de l'encodeur pour assurer la compatibilité
    # Un "one-hot encoding" est simulé en ajoutant des colonnes de zéros
    # pour les catégories manquantes et en remplissant les valeurs existantes.
    # On commence par créer des colonnes de zéros pour toutes les colonnes attendues par le modèle.
    input_df = pd.DataFrame(0, index=[0], columns=feature_columns)

    # Puis, on remplit les valeurs des colonnes numériques
    numerical_features = ['Age', 'Annual_Salary', 'Experience_Years', 'Spending_Score', 'Family_Size']
    for col in numerical_features:
        if col in input_data.columns:
            input_df[col] = input_data[col].values[0]

    # Et les colonnes catégorielles
    categorical_features = ['Gender', 'Country', 'Education_Level', 'Profession']
    for col in categorical_features:
        if col in input_data.columns:
            # Création du nom de la colonne encodée (par exemple, 'Gender_Male')
            col_name = f"{col}_{input_data[col].values[0]}"
            if col_name in input_df.columns:
                input_df[col_name] = 1

    # Prédiction avec le modèle
    prediction = model.predict(input_df)

    # Le modèle prédit 0 (faible valeur) ou 1 (grande valeur).
    # On convertit cette prédiction en une chaîne de caractères lisible.
    prediction_label = "High Value" if prediction[0] == 1 else "Low Value"

    return {"prediction": prediction_label}

# Point d'entrée de l'application pour le lancement
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
