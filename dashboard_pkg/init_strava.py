import webbrowser
import requests
import json

def main():
    print("=== Initialisation de l'autorisation Strava ===\n")

    client_id = input("➡️  Entrez votre client_id Strava : ").strip()
    client_secret = input("➡️  Entrez votre client_secret Strava : ").strip()

    redirect_uri = "http://localhost/exchange_token"
    scope = "read,activity:read_all"

    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={client_id}&response_type=code"
        f"&redirect_uri={redirect_uri}&approval_prompt=force&scope={scope}"
    )

    print("\n✅ Ouvrir ce lien dans votre navigateur pour autoriser l'application :\n")
    print(auth_url)

    webbrowser.open(auth_url)

    code = input("\n➡️  Une fois autorisé, copiez-collez ici le paramètre `code=` présent dans l’URL : ").strip()

    # Échange du code contre access_token et refresh_token
    print("\n🔁 Échange du code contre access_token / refresh_token...")
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    })

    if response.status_code != 200:
        print("❌ Erreur lors de l'échange :", response.text)
        return

    tokens = response.json()
    refresh_token = tokens.get("refresh_token")
    access_token = tokens.get("access_token")
    scope = tokens.get("scope", "inconnu")

    print(f"\n✅ Autorisation réussie avec scope : {scope}")
    print("➡️  Le refresh_token a été récupéré et sera enregistré.\n")

    # Sauvegarde dans strava_credentials.json
    creds = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    with open("strava_credentials.json", "w") as f:
        json.dump(creds, f, indent=2)

    # Optionnel : stocker l'access token aussi
    with open("strava.token", "w") as f:
        f.write(access_token)

    print("✅ Fichier strava_credentials.json et strava.token créés avec succès.")

if __name__ == "__main__":
    main()
