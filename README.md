# 📅 Dashboard Personnel – Tâches, Événements et Activités Strava (Todoist / Google Calendar / iCal INSA / Strava)

Ce projet regroupe plusieurs scripts pour extraire et visualiser les événements de vos calendriers personnels, les tâches terminées et vos activités sportives Strava, dans l’objectif de construire un **dashboard personnel automatisé**.

Il inclut également un générateur de **résumé quotidien** avec météo, tâches, événements et actualités, envoyé chaque matin par e-mail avec une version audio.

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
- `.env` (voir section configuration)

---

## 🔧 Dépendances (gérées automatiquement par Pipenv)
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- `todoist-api-python`
- `icalendar`, `pytz`, `requests`, `feedparser`
- `openai`, `gTTS`, `python-dotenv`

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

### `generate_daily_summary.py`
🧠 **Génère un résumé quotidien intelligent avec événements, tâches, météo et actualités**

- Utilise OpenAI (`gpt-3.5-turbo`) ou Hugging Face (`Mixtral-8x7B`) pour résumer
- Envoie le résumé par **email** avec une version **audio MP3** jointe
- Peut afficher une **notification locale** (via `plyer`, optionnel)

**Usage :**
```bash
python generate_daily_summary.py
```

#### Exemple de fichier `.env` :
```env
OPENAI_API_KEY=sk-...
HF_API_TOKEN=hf-...
EMAIL_SENDER=ton.email@gmail.com
EMAIL_PASSWORD=mot_de_passe_application
EMAIL_RECIPIENT=ton.email@gmail.com
```

> ⚠️ Utilise un [mot de passe d'application Gmail](https://support.google.com/accounts/answer/185833?hl=fr)

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

---

## 🚀 CLI centralisé & Version Web

Tous les scripts sont disponibles via la commande `dashboard` :

```bash
python dashboard.py <commande>
```

Commandes :
- gcal        : événements Google Calendar (aujourd’hui et cette semaine)
- ical        : événements iCal INSA (aujourd’hui et cette semaine)
- tasks       : tâches Todoist (à réaliser aujourd’hui et celles terminées cette semaine)
- strava      : activités Strava de la semaine
- daily       : résumé quotidien (envoi e-mail + audio)
- weekly      : résumé hebdomadaire (fichier + presse-papiers)
- serve       : version web (Flask, dépendance optionnelle)

Exemples :
```bash
python dashboard.py gcal
python dashboard.py daily
python dashboard.py serve --host 0.0.0.0 --port 8080
```

## 📂 Structure suggérée du projet
```
.
├── dashboard.py              # CLI central
├── dashboard_gui.py          # Version PySimpleGUI legacy (facultatif)
├── credentials.json
├── todoist.token
├── strava_credentials.json
├── strava.token
├── Pipfile / Pipfile.lock
├── .env
├── .gitignore
└── dashboard_pkg/
    ├── __init__.py
    ├── gcal.py
    ├── ical.py
    ├── extract_task_todoist.py
    ├── strava_utils.py
    ├── strava.py
    ├── init_strava.py
    ├── generate_daily_summary.py
    ├── get_todoist_mails.py
    ├── weekly_summary.py
    └── web.py
```

---

## 🕓 Automatisation (cron)
Exemple : lancer tous les jours à 7h du matin
```cron
0 7 * * * /chemin/vers/.venv/bin/python /chemin/vers/generate_daily_summary.py
```

---

## 🧠 TODO ou améliorations futures
- Export Markdown ou HTML
- Ajout de notifications mobiles (Pushbullet, Gotify...)
- Interface Web type Streamlit ou Flask

---

> Un assistant personnel simple, intelligent et entièrement personnalisable 🚀

