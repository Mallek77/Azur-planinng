# --- Connexion Google Sheets ---
@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://spreadsheets.google.com/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # On récupère les secrets directement dans le dictionnaire st.secrets
    # Assurez-vous que votre fichier secrets.toml est bien structuré comme [gcp_service_account]
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(creds)
    
    # Remplacez "Feuille de calcul sans titre" par le nom exact de votre fichier Google Sheets
    return gc.open("Feuille de calcul sans titre").sheet1

sheet = get_sheet()
