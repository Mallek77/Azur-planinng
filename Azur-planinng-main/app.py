"""
Azur Levage – Planning des interventions
Application Streamlit connectée à Google Sheets.
"""

import json
import locale
from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

APP_TITLE = "Azur Levage – Planning"
SHEET_NAME = "Azur-planing"
VALID_USERS = {"abdou", "mikel"}
VALID_PASSWORD = "Azur2026"

GOOGLE_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Ordre des colonnes dans Google Sheets
COLUMN_ORDER = ["Date", "Heure", "Durée", "Client", "Lieu", "Machine", "Prix (€)", "Coordonnées facturation"]


# ─────────────────────────────────────────────
# CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    layout="wide",
    page_title=APP_TITLE,
    page_icon="🏗️",
)


# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────

CSS_FILE = Path(__file__).resolve().parent / "style.css"


def inject_css() -> None:
    """Injecte le fichier style.css dans la page Streamlit."""
    css = CSS_FILE.read_text(encoding="utf-8").replace("</style>", "<\\/style>")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


inject_css()

# ─────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────

def init_session() -> None:
    """Initialise les clés de session si absentes."""
    st.session_state.setdefault("connecte", False)
    st.session_state.setdefault("utilisateur", "")


def show_login() -> None:
    """Affiche la page de connexion et gère l'authentification."""
    st.markdown(
        """
        <div class="login-hero">
            <div class="login-icon">🏗️</div>
            <h1>AZUR LEVAGE</h1>
            <p>Planning des interventions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        with st.form("login_form"):
            st.markdown('<p class="login-form-title">Connexion</p>', unsafe_allow_html=True)
            user = st.text_input("Identifiant", placeholder="Votre identifiant")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("SE CONNECTER", use_container_width=True, type="primary")

    if submitted:
        if user in VALID_USERS and password == VALID_PASSWORD:
            st.session_state.connecte = True
            st.session_state.utilisateur = user
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")


# ─────────────────────────────────────────────
# GOOGLE SHEETS
# ─────────────────────────────────────────────

@st.cache_resource(show_spinner="Connexion à Google Sheets…")
def get_sheet() -> gspread.Worksheet:
    """Retourne la première feuille du classeur Google Sheets."""
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds  = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, GOOGLE_SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def load_data(sheet: gspread.Worksheet) -> pd.DataFrame:
    """Charge toutes les lignes et retourne un DataFrame."""
    records = sheet.get_all_records()
    return pd.DataFrame(records) if records else pd.DataFrame()


def add_row(sheet: gspread.Worksheet, row: list) -> None:
    sheet.append_row(row)


def delete_row(sheet: gspread.Worksheet, row_index: int) -> None:
    """Supprime une ligne (index 1-based côté Sheets)."""
    sheet.delete_rows(row_index)


# ─────────────────────────────────────────────
# COMPOSANTS UI
# ─────────────────────────────────────────────

def show_header() -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <h1>🏗️ AZUR LEVAGE</h1>
            <p>Planning des interventions · Connecté en tant que
               <strong>{st.session_state.utilisateur.capitalize()}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_logout_button() -> None:
    if st.button("🚪 Déconnexion", key="btn_logout", type="secondary"):
        st.session_state.connecte   = False
        st.session_state.utilisateur = ""
        st.rerun()


def show_add_form(sheet: gspread.Worksheet) -> None:
    """Formulaire d'ajout d'une nouvelle mission."""
    with st.container(border=True):
        st.subheader("➕ Nouvelle mission")

        with st.form("form_ajout_mission", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                date = st.date_input("Date")
            with col2:
                heure = st.text_input("Heure", placeholder="08:00")
            with col3:
                duree = st.text_input("Durée", placeholder="2h ou 08:00-10:00")

            col4, col5 = st.columns(2)
            with col4:
                client = st.text_input("Client")
                machine = st.text_input("Machine")
            with col5:
                lieu = st.text_input("Lieu")
                prix = st.text_input("Prix (€)", placeholder="0.00")

            coord_fact = st.text_input("Coordonnées de facturation")

            submitted = st.form_submit_button("✅ Valider la mission", use_container_width=True)

        if submitted:
            row = [str(date), heure, duree, client, lieu, machine, prix, coord_fact]
            try:
                add_row(sheet, row)
                st.success("Mission ajoutée avec succès !")
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Impossible d'ajouter la mission : {exc}")


def show_planning_table(sheet: gspread.Worksheet) -> None:
    """Tableau des missions et suppression de ligne."""
    with st.container(border=True):
        st.subheader("📋 Planning en cours")

        try:
            df = load_data(sheet)
        except Exception as exc:
            st.error(f"❌ Erreur de lecture : {exc}")
            return

        if df.empty:
            st.info("Aucune intervention planifiée.")
        else:
            st.dataframe(df, use_container_width=True, height=320, hide_index=True)

            st.divider()
            st.caption("🗑️ Suppression d'une ligne")

            col_input, col_btn = st.columns([3, 1])
            with col_input:
                supp_id = st.number_input(
                    "Numéro de ligne à supprimer",
                    min_value=1,
                    max_value=len(df),
                    step=1,
                    label_visibility="collapsed",
                )
            with col_btn:
                if st.button("Supprimer", type="primary", use_container_width=True):
                    try:
                        delete_row(sheet, int(supp_id))
                        st.success(f"Ligne {supp_id} supprimée.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"❌ Suppression impossible : {exc}")


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

def main() -> None:
    init_session()

    # Tenter d'activer la locale FR (non bloquant)
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except Exception:
        pass

    # Authentification
    if not st.session_state.connecte:
        show_login()
        return

    # Connexion Google Sheets
    try:
        sheet = get_sheet()
    except Exception as exc:
        st.error(f"❌ Connexion Google Sheets impossible : {exc}")
        return

    # Interface principale
    show_header()
    show_logout_button()
    show_add_form(sheet)
    show_planning_table(sheet)


if __name__ == "__main__":
    main()
