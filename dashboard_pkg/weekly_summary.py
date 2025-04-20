import os
import glob
import pytz
from datetime import datetime
from dashboard_pkg.extract_task_todoist import get_all_tasks_from_this_week
from dashboard_pkg.strava import get_activities_this_week
from dashboard_pkg.gcal import get_credentials, get_week_events, format_event_time, build
from dashboard_pkg.ical import fetch_ical_events, get_week_events as get_week_events_ical, format_event_time as format_ical_time
import pyperclip
from dotenv import load_dotenv

# === PARAMÈTRES ===
TIMEZONE = pytz.timezone("Europe/Paris")

def get_latest_journal_entry():
    journal_files = sorted(glob.glob(os.path.expanduser("~/notes/journal/journal*.org")))
    if not journal_files:
        return "Aucun fichier journal trouvé."
    with open(journal_files[-1], "r", encoding="utf-8") as f:
        return f.read()

def get_gcal_events():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    # Load environment variables from .env file
    calendar_ids = {
        "Perso": os.getenv("CALENDAR_ID_PERSO"),
        "Pro": os.getenv("CALENDAR_ID_PRO"),
        "Famille": os.getenv("CALENDAR_ID_FAMILLE"),
    }
    events = get_week_events(service, calendar_ids)
    events.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date")))
    formatted = []
    for e in events:
        time_str = format_event_time(e)
        date = datetime.fromisoformat(e["start"].get("dateTime", e["start"].get("date"))).strftime("%A %d %B")
        formatted.append(f"{date} {time_str} ({e['calendar_name']})  {e['summary']}")
    return formatted

def get_ical_events():
    # Load environment variables from .env file
    ical_url = os.getenv("ICAL_URL")
    calendar = fetch_ical_events(ical_url)
    events = get_week_events_ical(calendar, TIMEZONE)
    events.sort(key=lambda e: e.get("dtstart").dt)
    formatted = []
    for e in events:
        date = e.get("dtstart").dt.strftime("%A %d %B")
        time_str = format_ical_time(e, TIMEZONE)
        summary = e.get("summary")
        formatted.append(f"{date} {time_str} {summary}")
    return formatted

def generate_summary():
    print("🔍 Chargement des variables d'environnement...")
    load_dotenv()
    print("📝 Lecture du journal...")
    journal = get_latest_journal_entry()

    print("✅ Récupération des tâches Todoist...")
    tasks, rapid_tasks = get_all_tasks_from_this_week()

    print("📆 Récupération des événements Google Calendar...")
    gcal_events = get_gcal_events()

    print("📅 Récupération des événements iCal INSA...")
    ical_events = get_ical_events()

    print("🏃‍♂️ Récupération des activités Strava...")
    strava_details, strava_time, strava_effort, strava_dist, strava_summary = get_activities_this_week()

    return f"""
🗓️ **Résumé Hebdomadaire**

---

📖 **Dernière entrée journal**  
{journal}

---

✅ **Tâches terminées (hors @rapide)**  
{chr(10).join(f"- {t}" for t in tasks)}

⚡ **Tâches @rapide**  
{chr(10).join(f"- {t}" for t in rapid_tasks)}

---

📆 **Événements Google Calendar**  
{chr(10).join(f"- {e}" for e in gcal_events)}

📅 **Événements iCal INSA**  
{chr(10).join(f"- {e}" for e in ical_events)}

---

🏃‍♂️ **Activités Strava**  
{chr(10).join(strava_details)}

⏱️ Temps total : {strava_time} | 📏 Distance : {strava_dist:.2f} km | 💪 Effort : {strava_effort}

📊 **Résumé par type**  
{chr(10).join(f"- {k}: {v['distance']:.1f} km en {v['duration']//3600}h{(v['duration']%3600)//60:02d}m" for k,v in strava_summary.items())}
"""

if __name__ == "__main__":
    summary = generate_summary()
    print(summary)
    with open("weekly_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    pyperclip.copy(summary)
    print("Résumé copié dans le presse-papiers.")
