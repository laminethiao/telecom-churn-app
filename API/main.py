from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI()

# Variables globales pour le modèle et les colonnes d'entraînement
model = None
training_columns = None

try:
    # Charger le modèle et les colonnes
    model = joblib.load("model/modele_random_forest.pkl")
    training_columns = joblib.load("model/training_columns.pkl")
    # Vérifier que le modèle a l'attribut feature_importances_
    if not hasattr(model, 'feature_importances_'):
        raise AttributeError("Le modèle chargé ne contient pas l'attribut 'feature_importances_'.")
except Exception as e:
    # Lève une erreur critique si le chargement échoue, l'API ne démarrera pas correctement
    raise RuntimeError(f"Erreur lors du chargement du modèle ou des colonnes: {str(e)}")

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
    try:
        # Convertir les données d'entrée en DataFrame pandas
        input_data = pd.DataFrame([data.dict()])

        # Encodage One-Hot des variables catégorielles
        input_encoded = pd.get_dummies(input_data)

        # Réindexer les colonnes pour correspondre aux colonnes d'entraînement du modèle
        # Les colonnes manquantes seront remplies avec 0, les colonnes supplémentaires seront ignorées
        input_encoded = input_encoded.reindex(columns=training_columns, fill_value=0)

        # Prédiction du churn
        prediction_raw = model.predict(input_encoded)[0]
        proba_raw = model.predict_proba(input_encoded)[0]

        # Obtenir la probabilité de la classe prédite
        class_index = model.classes_.tolist().index(prediction_raw)
        confidence = round(proba_raw[class_index] * 100, 2)

        # Message de prédiction
        prediction_message = "Le client va se désabonner" if prediction_raw == "Yes" else "Le client va rester"

        # Calcul des importances des caractéristiques
        # Assurez-vous que le modèle a bien cet attribut (e.g., RandomForestClassifier)
        feature_importances_data = None
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            # Créer un DataFrame pour trier et sélectionner les plus importantes
            feature_importance_df = pd.DataFrame({
                'Feature': training_columns, # Utiliser les colonnes d'entraînement comme noms de caractéristiques
                'Importance': importances
            }).sort_values(by='Importance', ascending=False)
            # Convertir en liste de dictionnaires pour la réponse JSON
            feature_importances_data = feature_importance_df.head(10).to_dict(orient='records') # Top 10

        return {
            "prediction": prediction_message,
            "probabilité": f"{confidence}%",
            "feature_importances": feature_importances_data # Inclure les importances
        }
    except Exception as e:
        # Gérer les erreurs de prédiction et renvoyer une réponse HTTP 400
        raise HTTPException(status_code=400, detail=f"Erreur lors de la prédiction: {str(e)}")

# Route racine pour vérifier que l'API est opérationnelle
@app.get("/")
def read_root():
    return {"message": "API de prédiction de churn opérationnelle"}

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet à votre application Streamlit (qui est sur une origine différente) de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (pour le développement)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes HTTP
)

# Point d'entrée pour lancer l'API avec Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

