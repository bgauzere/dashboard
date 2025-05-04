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