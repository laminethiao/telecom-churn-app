import streamlit as st
import time
import os
from pathlib import Path
st.set_page_config(
    page_title="Télécom Churn App",
    page_icon="📱",
    layout="wide"
)


# --- Importations du module d'authentification ---
from utils.auth import check_authentication



from utils.ui_style import set_background, custom_sidebar_style

# Configuration de la page

# Appliquer les styles UI
set_background()
custom_sidebar_style()

# --- NOUVEAU: Appel de la fonction d'authentification ---
check_authentication()


st.title("Bienvenue dans l'application de prédiction de Churn ! 👋")
st.markdown("""
    Utilisez la barre latérale pour naviguer vers le tableau de bord ou la page de prédiction.
""")

