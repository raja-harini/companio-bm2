import requests
import time
import os
import random
import io
import threading
from murf import Murf
from pydub import AudioSegment
from pydub.playback import play

# ------------------ CONFIG ------------------
MURF_API_KEY = "ap2_353f83f1-51b5-421e-b57d-5a817941e293"
TELEGRAM_BOT_TOKEN = "7722919054:AAFYKU9dSpg-i_xTBpFJk66qzHdwV0Hd8f0"
TELEGRAM_CHAT_ID = "6338596536"

VOICE_ID = "ta-IN-iniya"
murf_client = Murf(api_key=MURF_API_KEY)

# ------------------ FUNCTIONS ------------------
def get_health_data():
    return {
        "heart_rate": random.randint(50, 130),
        "temperature": round(random.uniform(35.5, 39.0), 1),
        "pulse": random.randint(50, 120)
    }

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.get(url, params=params)
    except Exception as e:
        print("[Telegram Error]", e)

def speak_alert_murf(message):
    def _play():
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

    # Run playback in separate thread so main loop continues
    threading.Thread(target=_play, daemon=True).start()

# ------------------ MAIN LOOP ------------------
print("📢 Tamil Health Alert System Running... Press CTRL+C to stop.")

try:
    while True:
        data = get_health_data()
        hr, temp, pulse = data["heart_rate"], data["temperature"], data["pulse"]

        print(f"💓 இதய துடிப்பு: {hr} BPM | 🌡 வெப்பநிலை: {temp}°C | 🫀 நாடி: {pulse} BPM")

        alerts = []
        if hr < 55 or hr > 120:
            alerts.append(f"இதய துடிப்பு இயல்பற்றது: {hr} BPM.")
        if temp < 36.0 or temp > 38.0:
            alerts.append(f"உடல் வெப்பநிலை இயல்பற்றது: {temp}°C.")
        if pulse < 55 or pulse > 110:
            alerts.append(f"நாடி வீச்சு இயல்பற்றது: {pulse} BPM.")

        if alerts:
            alert_text_tamil = "⚠ கவனம்! உங்கள் உடல்நிலை சரியில்லை. " + " ".join(alerts)
            print("🚨 ALERT:", alert_text_tamil)
            send_telegram_alert(alert_text_tamil)
            speak_alert_murf(alert_text_tamil)

        # Wait before next reading
        time.sleep(10)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
