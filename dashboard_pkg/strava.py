from datetime import datetime, timedelta
import locale
import requests
from collections import defaultdict
from dashboard_pkg.strava_utils import get_valid_access_token

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

def get_activities_this_week():
    access_token = get_valid_access_token()

    now = datetime.utcnow()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7) - timedelta(seconds=1)

    after_ts = int(start_of_week.timestamp())
    before_ts = int(end_of_week.timestamp())

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"after": after_ts, "before": before_ts, "per_page": 200}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Erreur API :", response.text)
        return []

    activities = response.json()
    formatted = []
    total_seconds = 0
    total_effort = 0
    total_distance = 0.0
    activity_types_summary = defaultdict(lambda: {"distance": 0.0, "duration": 0})

    for act in activities:
        name = act.get("name", "Sans nom")
        activity_type = act.get("type", "Inconnu")
        distance_km = act.get("distance", 0) / 1000.0
        duration_sec = act.get("moving_time", 0)
        effort = act.get("suffer_score", 0)
        if effort is None:
            effort = 0

        dt_str = act.get("start_date_local", "")
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", ""))
            date_str = dt.strftime("%A %d %B %Y %H:%M")
        except:
            date_str = dt_str

        h, m, s = duration_sec // 3600, (duration_sec % 3600) // 60, duration_sec % 60
        time_str = f"{h}h{m:02d}m{s:02d}s"

        formatted.append(
            f"Activité : {name}\n  Type : {activity_type}\n  Date : {date_str}\n  Distance : {distance_km:.2f} km\n  Durée : {time_str}\n  Mesure d'effort : {effort}"
        )

        total_seconds += duration_sec
        total_effort += effort
        total_distance += distance_km

        activity_types_summary[activity_type]["distance"] += distance_km
        activity_types_summary[activity_type]["duration"] += duration_sec

    total_h = total_seconds // 3600
    total_m = (total_seconds % 3600) // 60
    total_time_str = f"{total_h}h{total_m:02d}m"

    return formatted, total_time_str, total_effort, total_distance, activity_types_summary

if __name__ == '__main__':
    acts, total_time, total_effort, total_distance, activity_types = get_activities_this_week()
    print(f"\n{len(acts)} activités Strava cette semaine :\n")
    for a in acts:
        print(a)
        print("-" * 40)

    print(f"\n⏱️ Total temps de sport : {total_time}")
    print(f"📏 Distance totale : {total_distance:.2f} km")
    print(f"💪 Mesure totale d'effort : {total_effort}")

    print("\n📊 Résumé par type d'activité :")
    for act_type, stats in activity_types.items():
        h = stats["duration"] // 3600
        m = (stats["duration"] % 3600) // 60
        print(f"- {act_type}: {stats['distance']:.2f} km en {h}h{m:02d}m")
