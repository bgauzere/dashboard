"""
Web interface simple pour le dashboard (Flask).
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # Importer dynamiquement pour éviter les dépendances en cas d'utilisation CLI seule
    from dashboard_pkg.gcal import complete_today_events, format_event_time
    from dashboard_pkg.extract_task_todoist import get_tasks_due_today
    from dashboard_pkg.strava import get_activities_this_week

    # Récupérer les données
    events = complete_today_events()
    tasks = get_tasks_due_today()
    activities, total_time, total_effort, total_distance, _ = get_activities_this_week()

    # Construction du contenu HTML
    html = ['<html><head><meta charset="utf-8"><title>Dashboard Personnel</title></head><body>']
    html.append('<h1>Dashboard Personnel</h1>')
    html.append(f'<h2>Événements du jour ({len(events)})</h2><ul>')
    for e in events:
        html.append(f'<li>{format_event_time(e)} : {e.get("summary")} ({e.get("calendar_name")})</li>')
    html.append('</ul>')

    html.append(f'<h2>Tâches du jour ({len(tasks)})</h2><ul>')
    for t in tasks:
        html.append(f'<li>{t}</li>')
    html.append('</ul>')

    html.append(f'<h2>Activités Strava ({len(activities)})</h2>')
    html.append(f'<p>Total: {total_time}, Distance: {total_distance:.2f} km, Effort: {total_effort}</p><ul>')
    for a in activities:
        # Remplacer sauts de ligne par <br>
        item = a.replace('\n', '<br>')
        html.append(f'<li>{item}</li>')
    html.append('</ul>')

    html.append('</body></html>')
    return '\n'.join(html)