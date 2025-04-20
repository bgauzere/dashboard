#!/usr/bin/env python3
"""
Central CLI pour le dashboard personnel.
"""
import argparse
import runpy

def main():
    parser = argparse.ArgumentParser(
        prog='dashboard',
        description='CLI central pour le Dashboard Personnel'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('gcal', help='Afficher les événements Google Calendar (aujourd\'hui et cette semaine)')
    subparsers.add_parser('ical', help='Afficher les événements iCal INSA (aujourd\'hui et cette semaine)')
    subparsers.add_parser('tasks', help='Afficher les tâches Todoist (aujourd\'hui et complétées cette semaine)')
    subparsers.add_parser('strava', help='Afficher les activités Strava de la semaine')
    subparsers.add_parser('daily', help='Générer et envoyer le résumé quotidien')
    subparsers.add_parser('weekly', help='Générer le résumé hebdomadaire')
    serve_parser = subparsers.add_parser('serve', help='Démarrer la version web simple du dashboard')
    serve_parser.add_argument('--host', default='127.0.0.1', help='Adresse d\'écoute')
    serve_parser.add_argument('--port', default=5000, type=int, help='Port à utiliser')

    args = parser.parse_args()
    cmd = args.command

    if cmd == 'gcal':
        runpy.run_module('dashboard_pkg.gcal', run_name='__main__')
    elif cmd == 'ical':
        runpy.run_module('dashboard_pkg.ical', run_name='__main__')
    elif cmd == 'tasks':
        runpy.run_module('dashboard_pkg.extract_task_todoist', run_name='__main__')
    elif cmd == 'strava':
        runpy.run_module('dashboard_pkg.strava', run_name='__main__')
    elif cmd == 'daily':
        runpy.run_module('dashboard_pkg.generate_daily_summary', run_name='__main__')
    elif cmd == 'weekly':
        runpy.run_module('dashboard_pkg.weekly_summary', run_name='__main__')
    elif cmd == 'serve':
        try:
            from dashboard_pkg.web import app
        except ImportError:
            print("Flask n'est pas installé. Installez-le via 'pipenv install flask'.")
            return
        print(f"Démarrage du serveur web sur http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()