import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

# --- CONFIGURATION PAGE ---
st.set_page_config(
    layout="wide",
    page_title="Azur Levage – Planning",
    page_icon="🏗️"
)

# --- CSS (votre code original conservé) ---
st.markdown("""
<style>
/* (Votre CSS reste identique, je l'ai raccourci ici pour la lisibilité) */
.stApp { background-color: #f0f4f9 !important; }
</style>
""", unsafe_allow_html=True)

# ============================
# AUTHENTIFICATION
# ============================
if 'connecte' not in st.session_state:
    st.session_state.connecte = False
if 'utilisateur' not in st.session_state:
    st.session_state.utilisateur = ""

if not st.session_state.connecte:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        with st.form("login_form"):
            user = st.text_input("Identifiant", placeholder="Votre identifiant")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔐  SE CONNECTER")
        if submitted:
            if user in ("abdou", "mikel") and password == "Azur2026":
                st.session_state.connecte = True
                st.session_state.utilisateur = user
                st.rerun()
            else:
                st.error("❌ Identifiant ou mot de passe incorrect.")
    st.stop()

# ============================
# APP PRINCIPALE
# ============================

# --- Connexion Google Sheets (CORRIGÉE) ---
@st.cache_resource
def get_sheet():
    # Récupère les secrets depuis Streamlit Cloud
    creds_dict = st.secrets["gcp_service_account"]
    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Utilisation de from_json_keyfile_dict au lieu de from_json_keyfile_name
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(creds)
    return gc.open("Feuille de calcul sans titre").sheet1

sheet = get_sheet()

# --- HEADER & RESTE DE VOTRE APP ---
st.markdown(f"### 🏗️ AZUR LEVAGE - Planning pour {st.session_state.utilisateur.capitalize()}")

# Le reste de votre code (Formulaire + Tableau) reste identique...
# ...
