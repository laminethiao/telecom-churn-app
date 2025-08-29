from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import os

# Définition du modèle de données d'entrée
# Le modèle de données est adapté pour la prédiction de churn télécoms
class ChurnPredictionData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

# Initialisation de l'application FastAPI
app = FastAPI()

# Chargement du modèle et des colonnes d'entraînement
try:
    # Le chemin d'accès est relatif au dossier du projet
    # Le '..' permet de remonter d'un niveau si le script est exécuté depuis 'API/'
    # Cependant, la commande 'uvicorn API.main:app' est lancée depuis la racine du projet
    # donc le chemin 'model/' est correct
    model = joblib.load('model/modele_random_forest.pkl')
    training_columns = joblib.load('model/training_columns.pkl')
except FileNotFoundError as e:
    # Affiche une erreur claire si les fichiers ne sont pas trouvés
    print(f"Erreur: Fichier introuvable. Assurez-vous que les fichiers '.pkl' sont bien dans le sous-dossier 'model/'. Détails: {e}")
    model = None
    training_columns = None

# Nouvelle fonction pour extraire les importances des variables
def get_feature_importances(model, training_columns):
    """
    Extrait les importances des caractéristiques du modèle
    et les formate pour un retour JSON.
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feature_names = training_columns

        # Créer un DataFrame pour faciliter le tri et la visualisation
        feature_importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)

        # On retourne les 10 plus importantes sous forme de liste de dictionnaires pour l'API
        return feature_importance_df.head(10).to_dict('records')
    return None

# Endpoint de l'API pour la prédiction
@app.post("/predict")
def predict_churn(data: ChurnPredictionData):
    """
    Accepte les données d'un client et renvoie une prédiction de churn,
    ainsi que l'importance des variables.
    """
    if model is None or training_columns is None:
        return {"error": "Modèle ou colonnes d'entraînement non chargés. Vérifiez la présence des fichiers du modèle."}

    # Crée un DataFrame à partir des données de l'utilisateur
    input_df = pd.DataFrame([data.dict()])

    # Assurer que le DataFrame d'entrée a les mêmes colonnes que le DataFrame d'entraînement
    missing_cols = set(training_columns) - set(input_df.columns)
    for c in missing_cols:
        input_df[c] = 0

    input_df = input_df[training_columns]

    # Prédiction avec le modèle
    prediction_raw = model.predict(input_df)[0]
    proba_raw = model.predict_proba(input_df)[0]
    confidence = round(proba_raw[1] * 100, 2)  # La probabilité de la classe 'Yes'

    # Interprétation de la prédiction
    prediction_message = "Le client va se désabonner" if prediction_raw == "Yes" else "Le client va rester"

    # Récupérer les importances des variables
    feature_importances = get_feature_importances(model, training_columns)

    # Retourne la prédiction, la probabilité ET les importances des variables
    return {
        "prediction": prediction_message,
        "probabilité": f"{confidence:.2f}%",
        "feature_importances": feature_importances
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
