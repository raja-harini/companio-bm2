import requests
import time
import os
import random
import io
from murf import Murf
from pydub import AudioSegment
from pydub.playback import play
from deep_translator import GoogleTranslator

# ------------------ CONFIG ------------------
MURF_API_KEY = "ap2_353f83f1-51b5-421e-b57d-5a817941e293"
TELEGRAM_BOT_TOKEN = "7722919054:AAFYKU9dSpg-i_xTBpFJk66qzHdwV0Hd8f0"
TELEGRAM_CHAT_ID = "6338596536"

LANGUAGE = "Hindi"
VOICE_ID = "hi-IN-priya"
LANG_CODE = "hi"

murf_client = Murf(api_key=MURF_API_KEY)

# ------------------ FUNCTIONS ------------------
def get_health_data():
    return {
        "heart_rate": random.randint(50, 130),  
        "temperature": round(random.uniform(35.5, 39.0), 1),  
        "pulse": random.randint(50, 120)  
    }

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.get(url, params=params)

def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target=LANG_CODE).translate(text)
    except:
        return text

def speak_alert_murf(message):
    try:
        resp = murf_client.text_to_speech.generate(
            text=message,
            voice_id=VOICE_ID,
            format="WAV"
        )
        audio_data = requests.get(resp.audio_file).content
        seg = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
        play(seg)
    except Exception as e:
        print("[TTS Error]", e)

# ------------------ MAIN LOOP ------------------
while True:
    data = get_health_data()
    hr, temp, pulse = data["heart_rate"], data["temperature"], data["pulse"]

    print(f"💓 दिल की धड़कन: {hr} BPM | 🌡 तापमान: {temp}°C | 🫀 नाड़ी: {pulse} BPM")

    alerts = []
    if hr < 55 or hr > 120:
        alerts.append(f"दिल की धड़कन असामान्य है: {hr} BPM.")
    if temp < 36.0 or temp > 38.0:
        alerts.append(f"शरीर का तापमान असामान्य है: {temp}°C.")
    if pulse < 55 or pulse > 110:
        alerts.append(f"नाड़ी दर असामान्य है: {pulse} BPM.")

    if alerts:
        alert_text_hindi = "⚠ ध्यान दें! आपकी स्वास्थ्य स्थिति सामान्य नहीं है। " + " ".join(alerts)
        send_telegram_alert(alert_text_hindi)
        speak_alert_murf(alert_text_hindi)

    time.sleep(10)
