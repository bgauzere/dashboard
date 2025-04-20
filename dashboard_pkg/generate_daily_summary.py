import os
import pytz
from datetime import datetime
import feedparser
import requests
from openai import OpenAIError
from gtts import gTTS
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from dashboard_pkg.gcal import complete_today_events, format_event_time
from dashboard_pkg.ical import fetch_ical_events, get_day_events, format_event_time as format_ical_time
from dashboard_pkg.extract_task_todoist import get_tasks_due_today


def get_today_weather(lat=49.4431, lon=1.0993):
    print("Fetching weather data...")
    today = datetime.now().strftime("%Y-%m-%d")
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"precipitation_hours,precipitation_probability_max,weathercode"
        f"&timezone=Europe%2FParis&start_date={today}&end_date={today}"
    )
    resp = requests.get(url)
    data = resp.json()["daily"]
    t_min = data["temperature_2m_min"][0]
    t_max = data["temperature_2m_max"][0]
    pluie = data["precipitation_sum"][0]
    pluie_heures = data.get("precipitation_hours", [None])[0]
    pluie_proba = data.get("precipitation_probability_max", [None])[0]
    code = data["weathercode"][0]

    if code == 0:
        condition = "☀️ ciel clair"
    elif code in [1, 2, 3]:
        condition = "⛅ principalement clair à couvert"
    elif code in [45, 48]:
        condition = "🌫️ brouillard"
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        condition = "🌧️ pluie"
    elif code in [71, 73, 75, 77, 85, 86]:
        condition = "❄️ neige"
    elif code in [95, 96, 99]:
        condition = "⛈️ orage"
    else:
        condition = "🌡️ variable"

    print("Weather data fetched.")
    return (
        f"Météo du jour : {t_min} °C → {t_max} °C, précipitations : {pluie} mm, "
        f"heures de pluie : {pluie_heures} h, probabilité max : {pluie_proba} %, temps : {condition}"
    )

def summarize_with_huggingface(text):
    print("Utilisation de Hugging Face comme LLM alternatif...")
    url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN', '')}"}
    payload = {"inputs": text, "parameters": {"max_new_tokens": 300}}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"].split("\n", 1)[-1]
    else:
        return "(Erreur HuggingFace: résumé non disponible)"

def generate_audio(summary_text, filename="daily_summary.mp3"):
    tts = gTTS(text=summary_text, lang="fr")
    tts.save(filename)
    return filename

def send_email_with_summary(subject, body, attachment_path):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="audio", subtype="mpeg", filename="resume.mp3")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
        print("Résumé envoyé par e-mail !")

def generate_summary():
    # === Chargement des variables d'environnement ===
    load_dotenv()
    # === Configuration ===
    ICAL_TZ = pytz.timezone("Europe/Paris")

    gcal_events = complete_today_events()
    events_text = "\n".join([
        f"{format_event_time(e)} : ({e['calendar_name']}) {e['summary']}" for e in gcal_events
    ])
    ical_url = os.getenv("ICAL_URL")
    calendar = fetch_ical_events(ical_url)
    ical_events = get_day_events(calendar, ICAL_TZ)
    events_text += "\n" + "\n".join([
        f"{format_ical_time(e, ICAL_TZ)} : (INSA Pro) {e.get('summary')}" for e in ical_events
    ])

    print("Fetching tasks...")
    tasks = get_tasks_due_today()
    tasks_text = "\n".join(tasks)
    print("Tasks fetched.")

    print("Fetching weather and news...")
    try:
        weather_text = get_today_weather()
    except Exception as e:
        print(f"Erreur météo : {e}")
        weather_text = "Météo non disponible."
    try:
        news_text = "\n".join(get_today_news())
    except Exception as e:
        print(f"Erreur actualités : {e}")
        news_text = "Actualités non disponibles."
    print("Weather and news fetched.")
    with open("prompt", "r", encoding="utf-8") as file:
        prompt = file.read().strip()

    full_text = prompt + f"\n\n {weather_text}\n\n---\n\nÉvénements :\n{events_text}\n\n---\n\nTâches :\n{tasks_text}\n\n---\n\nActualités :\n{news_text}"
    print("Texte complet généré.")
    print(full_text)
    print("------")

    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": full_text}],
            temperature=0.7,
        )
        summary = response.choices[0].message.content
    except (Exception, OpenAIError) as e:
        print(f"Erreur OpenAI : {e}\nUtilisation de Hugging Face à la place...")
        summary = summarize_with_huggingface(full_text)
    
    print(summary)

    generate_and_send_summary(summary)

def get_today_news(rss_url="https://www.lemonde.fr/rss/une.xml", max_items=5):
    print("Fetching news...")
    feed = feedparser.parse(rss_url)
    news = []
    for entry in feed.entries[:max_items]:
        title = entry.title
        summary = entry.summary if 'summary' in entry else ''
        summary = summary.replace("\n", " ").strip()
        if len(summary) > 250:
            summary = summary[:247] + "..."
        news.append(f"🗞️ {title}\n   ↪ {summary}")
    print("News fetched.")
    return news

def generate_and_send_summary(summary_text):
    audio_path = generate_audio(summary_text)
    send_email_with_summary(
        subject=f"Résumé du {datetime.now().strftime('%A %d %B %Y')}",
        body=summary_text,
        attachment_path=audio_path
    )

if __name__ == "__main__":
    generate_summary()
