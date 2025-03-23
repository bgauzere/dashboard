# 📅 Dashboard Personnel – Tâches, Événements et Activités Strava (Todoist / Google Calendar / iCal INSA / Strava)

Ce projet regroupe plusieurs scripts pour extraire et visualiser les événements de vos calendriers personnels, les tâches terminées et vos activités sportives Strava, dans l’objectif de construire un **dashboard personnel automatisé**.

---

## 📦 Installation avec Pipenv

```bash
pipenv install
pipenv shell
```

Assurez-vous que les fichiers suivants soient présents :
- `credentials.json` (Google Calendar API)
- `todoist.token` (Token API Todoist)
- `strava_credentials.json` (Infos client_id / secret / refresh_token Strava)

---

## 🔧 Dépendances (gérées automatiquement par Pipenv)

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- `todoist-api-python`
- `icalendar`, `pytz`, `requests`

---

## 📁 Fichiers inclus

### `gcal.py`
📆 **Google Calendar – Récupère les événements du jour et de la semaine**

**Usage :**
```bash
python gcal.py
```
✅ Authentification automatique avec rafraîchissement via `~/.config/gcal_token.json`.

---

### `ical.py`
📅 **Calendrier iCal de l’INSA Rouen – Lecture des événements**

**Usage :**
```bash
python ical.py
```
✅ Télécharge et parse les événements iCal depuis l’URL de l’INSA. Affiche les événements de la journée et de la semaine.

---

### `extract_task_todoist.py`
✅ **Todoist – Liste des tâches terminées cette semaine (hors récurrentes)**

**Usage :**
```bash
python extract_task_todoist.py
```
🔍 Trie les tâches par date, et sépare les tâches taguées `@rapide`.

---

### Intégration Strava 🏃‍♂️
📈 **Récupération et affichage des activités Strava de la semaine**

#### `init_strava_authorization.py`
➡️ Initialise l’autorisation OAuth2 pour Strava et crée les fichiers nécessaires :
- `strava_credentials.json`
- `strava.token`

#### `strava_utils.py`
🔐 Gère automatiquement le rafraîchissement de l’access_token Strava.

#### `extract_strava.py`
📈 Récupère les activités Strava de la semaine et affiche :
- Nom de l’activité
- Type (course, vélo…)
- Date
- Distance
- Durée
- Mesure d'effort (suffer_score)

En fin de script :
- ⏱️ Temps total de sport
- 📏 Distance totale
- 💪 Effort cumulé
- 📊 Statistiques par type d’activité

---

## 🔐 Authentification

### 🔸 Google Calendar
- Crée un projet sur [Google Cloud Console](https://console.cloud.google.com/)
- Active l'API Calendar
- Crée des identifiants `credentials.json` (OAuth 2.0 Desktop App)

### 🔸 Todoist
- Génére un token API depuis [https://todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)
- Sauvegarde le dans un fichier `todoist.token`

### 🔸 Strava
1. Crée une application Strava sur [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
   - Renseigne **Authorization Callback Domain** : `localhost`

2. Lance le script d’autorisation :
```bash
python init_strava_authorization.py
```
   - Le script génère un lien d’autorisation avec les scopes `read,activity:read_all`
   - Ouvre le navigateur automatiquement
   - Tu colles le `code=` reçu dans le terminal
   - Il échange ce code contre un `refresh_token` stocké dans `strava_credentials.json`

📚 Plus d'infos :
- https://developers.strava.com/docs/authentication/
- https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities

---

## 📂 Structure suggérée du projet (mise à jour)
```
dashboard/
├── Pipfile
├── Pipfile.lock
├── credentials.json
├── todoist.token
├── gcal.py
├── ical.py
├── extract_task_todoist.py
├── extract_strava.py
├── strava_utils.py
├── init_strava_authorization.py
├── strava_credentials.json  ← généré automatiquement
└── strava.token             ← généré automatiquement
```

---

## 🚀 Prochaine étape : Intégration dans un dashboard web (Flask, Streamlit, etc.)

