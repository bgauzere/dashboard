import requests
from datetime import datetime, timedelta
from todoist_api_python.api import TodoistAPI
import locale

import requests
from datetime import datetime, timedelta
import locale

# Essayer de définir la locale
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')


def get_all_projects_map():
    """
    Récupère la liste des projets via le SDK Python officiel.
    Gère la pagination en parcourant les pages (listes) renvoyées.
    """
    try:
        with open('./todoist.token', 'r') as token_file:
            api_token = token_file.read().strip()
            
        api = TodoistAPI(api_token)
        projects_paginator = api.get_projects()
        
        project_map = {}
        
        # On itère sur le paginator (qui nous donne des "pages" / listes)
        for page in projects_paginator:
            # Si la page est bien une liste, on itère sur les projets à l'intérieur
            if isinstance(page, list):
                for project in page:
                    project_map[project.id] = project.name
            else:
                # Fallback au cas où le SDK changerait encore et renverrait l'objet direct
                project_map[page.id] = page.name
                
        return project_map
        
    except Exception as e:
        print(f"Exception lors de la récupération des projets via SDK: {e}")
        return {}
    
def get_all_tasks_from_this_week():
    with open('./todoist.token', 'r') as token_file:
        api_token = token_file.read().strip()
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    # 1. On charge la carte des projets (ID -> Nom) UNE SEULE FOIS au début
    project_map = get_all_projects_map()
    #project_map = get_all_projects_map(headers)

    # Définir les dates
    start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%dT00:00:00Z')
    end_date = datetime.now().strftime('%Y-%m-%dT23:59:59Z')

    parameters = {"limit": 200, "since": start_date, "until": end_date}
    
    # 2. Appel principal (celui qui marche maintenant)
    response = requests.get('https://api.todoist.com/api/v1/tasks/completed/by_completion_date', params=parameters, headers=headers)
    
    # Vérification de sécurité
    if response.status_code != 200:
        print(f"Erreur API Tasks: {response.text}")
        return [], []

    # Extraction des items (gestion de la structure de réponse qui peut varier légèrement)
    data = response.json()
    items = data.get('items', []) if isinstance(data, dict) else data

    tasks_this_week = [
        task for task in items
        if '@no_special_date' not in task.get('content', '')
    ]

    tasks_in_text = []
    
    # Tri par date
    # Note: Votre JSON montre 'completed_at' avec des microsecondes (.%f), donc on garde votre format de tri
    try:
        tasks_this_week.sort(key=lambda task: datetime.strptime(task['completed_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
    except ValueError:
        # Fallback si jamais le format change (sans microsecondes)
        tasks_this_week.sort(key=lambda task: task.get('completed_at'))

    for task in tasks_this_week:
        # --- OPTIMISATION : PLUS D'APPEL API ICI ---
        
        # 1. Récupérer la récurrence directement depuis l'objet task
        due_info = task.get('due')
        is_recurring = due_info.get('is_recurring') if due_info else False

        if not is_recurring:
            # 2. Récupérer le nom du projet via notre map locale
            p_id = task.get('project_id')
            project_name = project_map.get(str(p_id), "Projet inconnu")

            # Formatage de la date
            # On retire le 'Z' pour éviter les soucis sur certaines versions de Python
            date_str_raw = task['completed_at'].replace('Z', '')
            # On tronque les microsecondes si nécessaire pour strptime ou on utilise fromisoformat
            try:
                if '.' in date_str_raw:
                    completed_date = datetime.strptime(date_str_raw, '%Y-%m-%dT%H:%M:%S.%f')
                else:
                    completed_date = datetime.strptime(date_str_raw, '%Y-%m-%dT%H:%M:%S')
                
                formatted_date = completed_date.strftime('%A %d %B')
            except ValueError:
                formatted_date = task['completed_at']

            tasks_in_text.append(f"{task['content']}, Complétée le : {formatted_date} du projet : {project_name}")
    
    tasks_rapid = [task for task in tasks_in_text if '@rapide' in task]
    tasks = [task for task in tasks_in_text if '@rapide' not in task]
    
    return tasks, tasks_rapid

def get_tasks_due_today():
    with open('./todoist.token', 'r') as token_file:
        api_token = token_file.read().strip()
    api = TodoistAPI(api_token)

    today_str = datetime.now().date().isoformat()
    tasks_due_today = []

    # Retrieve all tasks and flatten any nested lists
    all_tasks = api.get_tasks()
    flattened_tasks = []
    for item in all_tasks:
        if isinstance(item, list):
            flattened_tasks.extend(item)
        else:
            flattened_tasks.append(item)
    # Filter tasks due today with safe attribute access
    for task in flattened_tasks:
        due = getattr(task, 'due', None)
        if due:
            time = None
            due_date = getattr(due, 'date', None) #can be a date or datetime
            if isinstance(due_date, datetime):
                time = due_date.time()
                due_date = due_date.date()
            #print(due_date.isoformat(),today_str)
            # test if  duedate is today
            if due_date == datetime.now().date():   
                priority_label = {
                    1: "🟢 Faible", 2: "🟡 Moyenne",
                    3: "🟠 Haute", 4: "🔴 Critique"
                }.get(getattr(task, 'priority', None), "Inconnue")
                content = getattr(task, 'content', str(task))
                if time:
                    content = f"à {time.strftime('%H:%M')} : {content}"
                tasks_due_today.append(f"{content} (Priorité : {priority_label})")
    # Sort tasks by priority
    tasks_due_today.sort(key=lambda task: task.split("Priorité : ")[-1])
    return tasks_due_today



if __name__ == '__main__':
    tasks_today = get_tasks_due_today()

    print(f"{len(tasks_today)} tâches à réaliser aujourd'hui:")
    for t in tasks_today:
        print(t)
        

    tasks, tasks_rapid = get_all_tasks_from_this_week()

    print(f"{len(tasks)} tâches réalisées:")
    for t in tasks:
        print(t)

    print(f"\n{len(tasks_rapid)} tâches rapides réalisées:")
    for t in tasks_rapid:
        print(t)