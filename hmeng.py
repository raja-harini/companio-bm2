import requests
import time
import os
import random
import tempfile
from murf import Murf
from pydub import AudioSegment
from pydub.playback import play
import io

# ------------------ CONFIG ------------------
MURF_API_KEY = "ap2_353f83f1-51b5-421e-b57d-5a817941e293"  # Your Murf API key
TELEGRAM_BOT_TOKEN = "7722919054:AAFYKU9dSpg-i_xTBpFJk66qzHdwV0Hd8f0"
TELEGRAM_CHAT_ID = "6338596536"

murf_client = Murf(api_key=MURF_API_KEY)

# ------------------ FUNCTIONS ------------------

# Function to get mock health data
def get_health_data():
    return {
        "heart_rate": random.randint(50, 130),  
        "temperature": round(random.uniform(35.5, 39.0), 1),  
        "pulse": random.randint(50, 120)  
    }

# Function to send Telegram alert
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.get(url, params=params)

# Speak alert using Murf TTS (real-time playback)
def speak_alert_murf(message):
    try:
        resp = murf_client.text_to_speech.generate(
            text=message,
            voice_id="en-IN-eashwar",  # English Indian Male Voice
            format="WAV"
        )
        audio_url = resp.audio_file
        audio_data = requests.get(audio_url).content
        audio_buf = io.BytesIO(audio_data)
        seg = AudioSegment.from_file(audio_buf, format="wav")
        play(seg)
    except Exception as e:
        print("[TTS Error]", e)

# ------------------ MAIN LOOP ------------------
while True:
    health_data = get_health_data()
    
    heart_rate = health_data["heart_rate"]
    temperature = health_data["temperature"]
    pulse = health_data["pulse"]

    print(f"💓 Heart Rate: {heart_rate} BPM | 🌡 Temperature: {temperature}°C | 🫀 Pulse: {pulse} BPM")

    alerts = []
    if heart_rate < 55 or heart_rate > 120:
        alerts.append(f"Heart Rate is abnormal: {heart_rate} BPM.")
    if temperature < 36.0 or temperature > 38.0:
        alerts.append(f"Temperature is abnormal: {temperature}°C.")
    if pulse < 55 or pulse > 110:
        alerts.append(f"Pulse Rate is abnormal: {pulse} BPM.")

    if alerts:
        alert_message = "\n".join(alerts)
        print("🚨 ALERT:", alert_message)

        # Send alert to Telegram
        send_telegram_alert(alert_message)

        # Speak alert via Murf
        english_voice_message = "Attention! Your health condition is not normal. " + " ".join(alerts)
        speak_alert_murf(english_voice_message)

    time.sleep(10)
