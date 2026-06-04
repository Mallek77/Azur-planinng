import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- CONFIGURATION PAGE ---
st.set_page_config(
    layout="wide",
    page_title="Azur Levage – Planning",
    page_icon="🏗️"
)

# --- CSS UNIFIÉ ET OPTIMISÉ ---
st.markdown("""
<style>
/* ============================
   IMPORTS & VARIABLES
============================ */
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@700&display=swap');

:root {
    --navy:      #0b2e59;
    --navy-mid:  #0d3872;
    --navy-light:#1a4f9c;
    --accent:    #1877f2;   /* Facebook blue – boutons */
    --accent-hov:#145db8;
    --bg:        #f0f4f9;
    --card:      #ffffff;
    --border:    #ccd8ea;
    --text:      #0b2e59;
    --muted:     #6b87a8;
    --danger:    #d93025;
    --success:   #1e7e34;
    --radius:    10px;
    --shadow:    0 4px 20px rgba(11,46,89,.12);
}

/* ============================
   RESET STREAMLIT GLOBALS
============================ */
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif !important;
}
.stApp {
    background-color: var(--bg) !important;
}
/* Supprimer le padding haut Streamlit */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}
/* Masquer le bouton "Show password" (icône œil) */
button[aria-label="Show password"],
button[data-testid="passwordInputVisibilityToggle"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}
/* Masquer le menu hamburger & footer */
#MainMenu, footer, header { visibility: hidden; }

/* ============================
   TITRES
============================ */
h1, h2, h3 {
    color: var(--navy) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: .5px;
}
h1 { font-size: 2rem !important; }
h2, h3 { font-size: 1.3rem !important; }

/* ============================
   PAGE DE CONNEXION
============================ */
.login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 85vh;
}
.auth-card {
    background: var(--card);
    border: 2px solid var(--navy);
    border-radius: 16px;
    box-shadow: var(--shadow);
    padding: 48px 40px;
    width: 100%;
    max-width: 420px;
    text-align: center;
}
.auth-card .logo-text {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.auth-card .logo-sub {
    font-size: .85rem;
    color: var(--muted);
    margin-bottom: 32px;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.auth-card .lock-icon {
    font-size: 2.5rem;
    margin-bottom: 16px;
}
.auth-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--navy), transparent);
    margin: 20px 0;
    border: none;
}

/* ============================
   CHAMPS DE SAISIE
============================ */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    background-color: #fafcff !important;
    font-family: 'Barlow', sans-serif !important;
    padding: 8px 14px !important;
    transition: border-color .2s;
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(11,46,89,.1) !important;
    outline: none !important;
}
/* Labels */
.stTextInput label,
.stDateInput label,
.stNumberInput label,
.stSelectbox label {
    color: var(--navy) !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
}

/* ============================
   BOUTONS
============================ */
div.stButton > button,
div.stFormSubmitButton > button {
    background-color: var(--accent) !important;
    color: #ffffff !important;
    width: 100% !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: .95rem !important;
    letter-spacing: .5px;
    border: none !important;
    padding: 11px 20px !important;
    cursor: pointer !important;
    transition: background-color .2s, transform .1s, box-shadow .2s !important;
    box-shadow: 0 2px 8px rgba(24,119,242,.3) !important;
}
div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background-color: var(--accent-hov) !important;
    box-shadow: 0 4px 16px rgba(24,119,242,.45) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active,
div.stFormSubmitButton > button:active {
    transform: translateY(0) !important;
}

/* Bouton suppression */
div.stButton > button.danger-btn {
    background-color: var(--danger) !important;
    box-shadow: 0 2px 8px rgba(217,48,37,.3) !important;
}

/* ============================
   FORMULAIRE / CARDS
============================ */
.form-card, .table-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 24px;
    box-shadow: var(--shadow);
}
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--navy);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--navy);
}

/* ============================
   HEADER
============================ */
.app-header {
    display: flex;
    align-items: center;
    gap: 20px;
    background: var(--navy);
    border-radius: 14px;
    padding: 18px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(11,46,89,.25);
}
.app-header .app-title {
    font-family: 'Barlow Condensed', sans-serif;
    color: #ffffff;
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 0;
}
.app-header .app-subtitle {
    color: rgba(255,255,255,.65);
    font-size: .85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
}
.header-badge {
    margin-left: auto;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.25);
    color: #fff;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: 1px;
}

/* ============================
   DATAFRAME
============================ */
.stDataFrame {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ============================
   SÉPARATEUR
============================ */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
}

/* ============================
   ALERTES
============================ */
.stAlert {
    border-radius: var(--radius) !important;
}
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
    # Centrage via colonnes Streamlit
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div class="auth-card">
            <div class="lock-icon">🏗️</div>
            <div class="logo-text">AZUR LEVAGE</div>
            <div class="logo-sub">Espace de gestion</div>
            <hr class="auth-divider">
        </div>
        """, unsafe_allow_html=True)

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

# --- Connexion Google Sheets ---
@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = gspread.authorize(creds)
    return gc.open("Feuille de calcul sans titre").sheet1

sheet = get_sheet()

# --- HEADER ---
st.markdown(f"""
<div class="app-header">
    <div>
        <p class="app-title">🏗️ AZUR LEVAGE</p>
        <p class="app-subtitle">Planning des interventions</p>
    </div>
    <div class="header-badge">👤 {st.session_state.utilisateur.capitalize()}</div>
</div>
""", unsafe_allow_html=True)

# Bouton déconnexion discret
col_spacer, col_logout = st.columns([5, 1])
with col_logout:
    if st.button("🚪 Déconnexion"):
        st.session_state.connecte = False
        st.session_state.utilisateur = ""
        st.rerun()

# --- COLONNES PRINCIPALES ---
col_form, col_table = st.columns([1, 2.2], gap="large")

# ---- FORMULAIRE ----
with col_form:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ Nouvelle Mission</div>', unsafe_allow_html=True)

    with st.form("ajout_mission"):
        date    = st.date_input("📅 Date")
        heure   = st.text_input("🕐 Heure", placeholder="ex : 08h30")
        client  = st.text_input("🏢 Client", placeholder="Nom du client")
        lieu    = st.text_input("📍 Lieu", placeholder="Adresse / Ville")
        machine = st.text_input("🏗️ Machine", placeholder="Type de grue / engin")
        prix    = st.text_input("💶 Prix (€)", placeholder="ex : 1 200 €")

        valider = st.form_submit_button("✅  VALIDER L'INTERVENTION")

    if valider:
        sheet.append_row([str(date), heure, client, lieu, machine, prix])
        st.success("✅ Intervention ajoutée avec succès !")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---- TABLEAU ----
with col_table:
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Planning en cours</div>', unsafe_allow_html=True)

    data = sheet.get_all_records()

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=420)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**🗑️ Supprimer une ligne**")
        col_num, col_btn = st.columns([2, 1])
        with col_num:
            supp_id = st.number_input(
                "Numéro de ligne",
                min_value=1,
                max_value=len(df),
                step=1,
                label_visibility="collapsed"
            )
        with col_btn:
            if st.button("🗑️  SUPPRIMER", key="del"):
                sheet.delete_rows(int(supp_id) + 1)
                st.warning(f"Ligne {supp_id} supprimée.")
                st.rerun()
    else:
        st.info("📭 Aucune intervention planifiée pour le moment.")

    st.markdown('</div>', unsafe_allow_html=True)