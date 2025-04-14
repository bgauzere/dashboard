from todoist_api_python.api import TodoistAPI

api = TodoistAPI("8ea3fe98d6f0a7902a14b807a529327634cde8c8")

try:
    projects = api.get_projects()
    print(projects[0])
except Exception as error:
    print(error)
