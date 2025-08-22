import os
import requests
import joblib
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# Initialisation de l'application FastAPI
app = FastAPI()

# URLs pour télécharger le modèle et les colonnes d'entraînement depuis Google Drive.
# Ces URLs ont été modifiées pour permettre un téléchargement direct.
MODEL_URL = "https://drive.google.com/uc?export=download&id=1XuEraj-uIGymTORYwJ65r2tTOwTv09wh"
COLUMNS_URL = "https://drive.google.com/uc?export=download&id=1Wr6lagz3Wp6crOs81RzdycNs4DBagQJs"

# Variables pour le modèle et les colonnes, initialisées à None
model = None
training_columns = None


def download_file(url: str, filename: str):
    """
    Télécharge un fichier depuis une URL et le sauvegarde localement.
    Cette fonction est essentielle pour récupérer le modèle et les colonnes.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP 4xx/5xx
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Fichier {filename} téléchargé avec succès.")
    except Exception as e:
        # En cas d'échec, on lève une erreur critique pour arrêter le déploiement
        raise RuntimeError(f"Erreur lors du téléchargement de {filename}: {str(e)}")


# Fonction qui s'exécute au démarrage de l'application Vercel
@app.on_event("startup")
def load_resources():
    global model, training_columns
    try:
        # Crée un dossier temporaire pour stocker les fichiers téléchargés
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # Définir les chemins de fichiers locaux
        model_path = "temp/modele_random_forest.pkl"
        columns_path = "temp/training_columns.pkl"

        # Télécharger et charger le modèle et les colonnes
        download_file(MODEL_URL, model_path)
        download_file(COLUMNS_URL, columns_path)

        model = joblib.load(model_path)
        training_columns = joblib.load(columns_path)

        # Vérification de l'attribut du modèle pour s'assurer qu'il est correct
        if not hasattr(model, 'feature_importances_'):
            raise AttributeError("Le modèle chargé ne contient pas 'feature_importances_'.")

        print("Modèle et colonnes chargés avec succès au démarrage de l'application.")
    except Exception as e:
        # Afficher l'erreur sans arrêter le serveur, mais en indiquant l'échec
        print(f"Échec critique du chargement des ressources: {str(e)}")


# Pydantic model pour les données d'entrée du client
class ClientData(BaseModel):
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


# Route de prédiction
@app.post("/predict")
def predict(data: ClientData):
    global model, training_columns
    # S'assurer que le modèle est bien chargé avant de tenter une prédiction
    if model is None or training_columns is None:
        raise HTTPException(status_code=503, detail="Le modèle n'est pas encore chargé. Veuillez réessayer.")

    try:
        input_data = pd.DataFrame([data.dict()])
        input_encoded = pd.get_dummies(input_data)
        input_encoded = input_encoded.reindex(columns=training_columns, fill_value=0)

        # Prédiction et calcul des probabilités
        prediction_raw = model.predict(input_encoded)[0]
        proba_raw = model.predict_proba(input_encoded)[0]
        class_index = model.classes_.tolist().index(prediction_raw)
        confidence = round(proba_raw[class_index] * 100, 2)

        prediction_message = "Le client va se désabonner" if prediction_raw == "Yes" else "Le client va rester"

        feature_importances_data = None
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance_df = pd.DataFrame({
                'Feature': training_columns,
                'Importance': importances
            }).sort_values(by='Importance', ascending=False)
            feature_importances_data = feature_importance_df.head(10).to_dict(orient='records')

        return {
            "prediction": prediction_message,
            "probabilité": f"{confidence}%",
            "feature_importances": feature_importances_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la prédiction: {str(e)}")


# Route racine
@app.get("/")
def read_root():
    return {"message": "API de prédiction de churn opérationnelle"}


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Point d'entrée pour le développement local
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
