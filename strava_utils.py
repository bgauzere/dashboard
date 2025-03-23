import requests
import json
import os

STRAVA_TOKEN_FILE = "strava.token"
STRAVA_CREDENTIALS_FILE = "strava_credentials.json"

def get_valid_access_token():
    """
    Rafraîchit automatiquement l'access token Strava si nécessaire.
    Les credentials doivent être dans un fichier JSON : strava_credentials.json
    """
    if not os.path.exists(STRAVA_CREDENTIALS_FILE):
        raise FileNotFoundError(
            "Fichier strava_credentials.json manquant. "
            "Ajoute un fichier contenant : client_id, client_secret, refresh_token"
        )

    with open(STRAVA_CREDENTIALS_FILE, "r") as f:
        creds = json.load(f)

    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    refresh_token = creds.get("refresh_token")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Le fichier strava_credentials.json est incomplet.")

    # Appel à l'API Strava pour rafraîchir l'access token
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    })

    if response.status_code != 200:
        raise RuntimeError(f"Erreur lors du rafraîchissement du token : {response.text}")

    tokens = response.json()
    access_token = tokens.get("access_token")
    new_refresh_token = tokens.get("refresh_token")

    # Optionnel : si le refresh token a changé, on met à jour le fichier
    if new_refresh_token and new_refresh_token != refresh_token:
        creds["refresh_token"] = new_refresh_token
        with open(STRAVA_CREDENTIALS_FILE, "w") as f:
            json.dump(creds, f, indent=2)

    # Sauvegarde le nouvel access_token dans strava.token
    with open(STRAVA_TOKEN_FILE, "w") as f:
        f.write(access_token)

    return access_token
