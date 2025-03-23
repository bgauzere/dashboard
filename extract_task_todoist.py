import requests
from datetime import datetime, timedelta
from todoist_api_python.api import TodoistAPI
import locale

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

def is_recurring_and_project_name(task, headers):
    item_id = task.get("v2_task_id")
    item_parameters = {"item_id": item_id, "all_data": True}
    item_response = requests.post('https://api.todoist.com/sync/v9/items/get', json=item_parameters, headers=headers)
    json_response = item_response.json()

    item = json_response.get('item')
    project = json_response.get('project', {})

    if item:
        due = item.get('due')
        is_recurring = due.get('is_recurring') if due else False
        project_name = project.get('name', 'Inconnu')
        return is_recurring, project_name
    else:
        return False, project.get('name', 'Inconnu')

def get_all_tasks_from_this_week():
    with open('./todoist.token', 'r') as token_file:
        api_token = token_file.read().strip()
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    # Définir les dates de début et de fin (cette semaine)
    start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%dT00:00:00Z')
    end_date = datetime.now().strftime('%Y-%m-%dT23:59:59Z')

    parameters = {"limit": 200, "since": start_date, "until": end_date}
    response = requests.post('https://api.todoist.com/sync/v9/completed/get_all', json=parameters, headers=headers)
    tasks_this_week = [
        task for task in response.json().get('items', [])
        if '@no_special_date' not in task.get('content', '')
    ]
    tasks_in_text = []
    tasks_this_week.sort(key=lambda task: datetime.strptime(task['completed_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
    for task in tasks_this_week:
        is_recurring, project_name = is_recurring_and_project_name(task,headers)
        if not(is_recurring):
            # Set the locale to French
            
            completed_date = datetime.strptime(task['completed_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = completed_date.strftime('%A %d %B')
            tasks_in_text.append(f"{task['content']}, Complétée le : {formatted_date} du projet : {project_name}")
        # Exemple de récupération d'une tâche spécifique avec son ID
    
    tasks_rapid = [task for task in tasks_in_text if '@rapide' in task]
    tasks = [task for task in tasks_in_text if '@rapide' not in task]
    return tasks, tasks_rapid
if __name__ == '__main__':
    tasks, tasks_rapid = get_all_tasks_from_this_week()

    print(f"{len(tasks)} tâches réalisées:")
    for t in tasks:
        print(t)

    print(f"\n{len(tasks_rapid)} tâches rapides réalisées:")
    for t in tasks_rapid:
        print(t)