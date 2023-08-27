# from stationmeteo.stationmeteo import ServeurMaison
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime
import PySimpleGUI as sg
import csv
import sys
from ics import Calendar
from datetime import date
import caldav
import requests
from todoist_api_python.api import TodoistAPI

matplotlib.use('TkAgg')


def todo_content():
    api = TodoistAPI("8ea3fe98d6f0a7902a14b807a529327634cde8c8")
    tasks = api.get_tasks(filter="today")
    todolist = [task.content for task in tasks]
    return todolist


def agenda_content_baikal():
    url = "https://benauit.nohost.me:443/baikal/cal.php/calendars/benoit/default/"
    user = "benoit"
    password = "Bwarel0!"

    today = datetime.today()
    events_str = []

    with caldav.DAVClient(url=url, username=user, password=password) as client:
        my_principal = client.principal()
        calendars = my_principal.calendars()
        for calendar in calendars:
            events = calendar.date_search(
                start=today.replace(hour=0, minute=0),
                end=today.replace(hour=23, minute=59), expand=False)
            for e in events:
                description = e.vobject_instance.vevent.summary.value
                date_debut = f"{e.instance.vevent.dtstart.value:%H:%M}"
                events_str.append(f"  • {description} à {date_debut}")
    return events_str


def agenda_content_insa():
    events_str = []
    with open("./ADECal.ics") as calendar_file:
        c = Calendar(calendar_file.read())
        today_event = [e for e in list(
            c.timeline) if e.begin.date() == date.today()]
        for e in today_event:
            events_str.append(f"  • {e.name} à {e.begin.format('HH:mm')}")
    return events_str


def agenda_content():
    events_str = agenda_content_baikal()
    events_str = events_str + agenda_content_insa()
    if len(events_str) == 0:
        return ["Rien pour aujourd'hui !"]

    return events_str


# def meteo_content():
#     serveur = ServeurMaison()
#     data_meteo = serveur.get_data()
#     str_meteo = ""
#     for id_source, data_source in data_meteo.items():
#         for donnee in data_source:
#             str_meteo = str_meteo + (f"{donnee} ")
#     return str_meteo


def inbox_content():
    with open('/home/bgauzere/notes/postit.org') as inbox_file:
        content = inbox_file.read()
        return content


def draw_figure(canvas):
    poids = []
    dates = []
    with open('/home/bgauzere/Documents/Santé/poids.csv', newline='') as csvfile:
        poids_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in poids_csv:
            dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
            poids.append(float(row[1]))

    x = range(len(poids))
    fig, ax = plt.subplots(figsize=(10, 3))
    lowess = sm.nonparametric.lowess(poids, x, frac=0.4)
    ax.plot(dates, poids, "o", markersize=5)
    ax.plot(dates, lowess[:, 1], linewidth=3)
    ax.plot([dates[0], dates[-1]], [75, 75], '--')
    ax.tick_params(axis="x", which="both", rotation=45, labelsize=10)
    ax.tick_params(axis="y", which="both", labelsize=10)
    ax.spines["top"].set_color("None")
    ax.spines["right"].set_color("None")
    ax.grid()
    fig.tight_layout()
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


theme_dict = {'BACKGROUND': '#2B475D',
              'TEXT': '#FFFFFF',
              'INPUT': '#F2EFE8',
              'TEXT_INPUT': '#000000',
              'SCROLL': '#F2EFE8',
              'BUTTON': ('#000000', '#C2D4D8'),
              'PROGRESS': ('#FFFFFF', '#C7D5E0'),
              'BORDER': 1, 'SLIDER_DEPTH': 1, 'PROGRESS_DEPTH': 1}

# sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#C7D5E0'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = 2
BPAD_LEFT = 2
BPAD_LEFT_INSIDE = 2
BPAD_RIGHT = 2

date_today = datetime.today()

top_banner = [[sg.Text('Dashboard', font='Any 30', background_color=DARK_HEADER_COLOR),
               sg.Text(f"{date_today:%d %B %y}", font='Any 20', background_color=DARK_HEADER_COLOR, expand_x=True, justification="right")]]


block_meteo = [[sg.Text('Meteo', size=(50, 1), pad=BPAD_TOP, font='Any 20')],
               [sg.Text("Travaux en Cours", font='Roboto 15')]]
# [sg.Text(meteo_content(), font='Roboto 15')]]

content = inbox_content()
block_notes = [[sg.Text('Notes', font='Any 20')],
               [sg.Text(content)]]


block_todo = [[sg.Text('TODO du jour', font='Any 20')]]
for todo in todo_content():
    block_todo.append([sg.T(f"  •{todo}", font='Any 10')])

block_agenda = [[sg.Text('Agenda', font='Any 20')]]
for event in agenda_content():
    block_agenda.append([sg.T(event, font='Any 10')])

block_poids = [[sg.Text('Poids', font='Any 20')],
               [sg.Canvas(key='-CANVAS-')]]


layout = [[sg.Column(top_banner, size=(1024, 60), pad=BPAD_TOP, background_color=DARK_HEADER_COLOR)],
          #          [sg.Column(block_meteo, size=(1024, 75), pad=BPAD_TOP)],
          [sg.Column(block_notes, size=(1024, 200), pad=BPAD_TOP,
                     scrollable=True,  vertical_scroll_only=True)],
          [sg.Column(block_todo, size=(512, 200), pad=BPAD_LEFT),
           sg.Column(block_agenda, size=(512, 200),  pad=BPAD_RIGHT)],
          [sg.Column(block_poids, size=(1024, 350), pad=BPAD_TOP)],
          ]

window = sg.Window('Dashboard PySimpleGUI-Style', layout,  # margins=(0, 0),
                   background_color=BORDER_COLOR, no_titlebar=False, grab_anywhere=True,
                   finalize=True)
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas)

while True:             # Event Loop
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
window.close()
