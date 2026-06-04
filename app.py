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

# --- CSS ---
st.markdown("""
<style>
.stApp { background-color: #f0f4f9 !important; }
.app-header { background: #0b2e59; padding: 20px; border-radius: 14px; color: white; margin-bottom: 24px; }
.form-card, .table-card { background: white; padding: 28px; border-radius: 14px; box-shadow: 0 4px 20px rgba(11,46,89,.12); }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
if 'connecte' not in st.session_state:
    st.session_state.connecte = False
if 'utilisateur' not in st.session_state:
    st.session_state.utilisateur = ""

if not st.session_state.connecte:
    st.markdown("<div style='text-align:center'><h1>🏗️ AZUR LEVAGE</h1></div>", unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("SE CONNECTER"):
            if user in ("abdou", "mikel") and password == "Azur2026":
                st.session_state.connecte = True
                st.session_state.utilisateur = user
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
    st.stop()

# --- CONNEXION GOOGLE SHEETS ---
@st.cache_resource
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("azur-planning").sheet1  # ← mets le vrai nom de ton fichier Google Sheets

try:
    sheet = get_sheet()
except Exception as e:
    st.error(f"❌ Erreur de connexion Google Sheets : {e}")
    st.stop()

# --- APP PRINCIPALE ---
st.markdown(f"""
<div class="app-header">
    <h1>🏗️ AZUR LEVAGE</h1>
    <p>Planning des interventions - Utilisateur : {st.session_state.utilisateur.capitalize()}</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚪 Déconnexion"):
    st.session_state.connecte = False
    st.rerun()

col_form, col_table = st.columns([1, 2.2], gap="large")

with col_form:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.subheader("➕ Nouvelle Mission")
    with st.form("ajout_mission"):
        date = st.date_input("Date")
        heure = st.text_input("Heure")
        client = st.text_input("Client")
        lieu = st.text_input("Lieu")
        machine = st.text_input("Machine")
        prix = st.text_input("Prix (€)")
        if st.form_submit_button("VALIDER"):
            sheet.append_row([str(date), heure, client, lieu, machine, prix])
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_table:
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.subheader("📋 Planning en cours")
    try:
        data = sheet.get_all_records()
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        data = []
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        supp_id = st.number_input("Numéro de ligne à supprimer", min_value=1, max_value=len(df), step=1)
        if st.button("SUPPRIMER"):
            sheet.delete_rows(int(supp_id) + 1)
            st.rerun()
    else:
        st.info("Aucune intervention.")
    st.markdown('</div>', unsafe_allow_html=True)