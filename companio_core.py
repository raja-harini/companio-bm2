# companio_core.py
import os, io, time, threading
from dotenv import load_dotenv
load_dotenv()
import requests
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from openai import OpenAI
from murf import Murf
from deep_translator import GoogleTranslator

# config from env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MURF_API_KEY = os.getenv("MURF_API_KEY")

if not OPENROUTER_API_KEY or not MURF_API_KEY:
    raise RuntimeError("Set OPENROUTER_API_KEY and MURF_API_KEY in .env")

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
murf_client = Murf(api_key=MURF_API_KEY)

voice_map = {
    "English": "en-IN-eashwar",
    "Tamil": "ta-IN-iniya",
    "Hindi": "hi-IN-priya"
}
lang_code_map = {"English":"en","Tamil":"ta","Hindi":"hi"}

def listen(language="English", timeout=8):
    r = sr.Recognizer()
    with sr.Microphone() as src:
        print(f"[listen] ambient adjust...")
        r.adjust_for_ambient_noise(src, duration=0.5)
        print(f"[listen] Listening ({language})...")
        audio = r.listen(src, phrase_time_limit=timeout)
    try:
        code = "en-IN" if language=="English" else ("ta-IN" if language=="Tamil" else "hi-IN")
        return r.recognize_google(audio, language=code)
    except Exception as e:
        print("[STT Error]", e)
        return None

def ask_gemini(prompt):
    try:
        resp = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={"HTTP-Referer": "https://companio.ai","X-Title":"CompanioBot"}
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[LLM ERROR] {e}"

def speak_murf_live(text, voice_id):
    try:
        resp = murf_client.text_to_speech.generate(text=text, voice_id=voice_id, format="WAV")
        audio_url = resp.audio_file
        audio_data = requests.get(audio_url).content
        audio_buf = io.BytesIO(audio_data)
        seg = AudioSegment.from_file(audio_buf, format="wav")
        play(seg)
    except Exception as e:
        print("[TTS Error]", e)

def translate_if_needed(text, language):
    code = lang_code_map.get(language,"en")
    if code=="en": return text
    return GoogleTranslator(source='auto', target=code).translate(text)

def run_assistant(language="English", stop_event: threading.Event=None):
    """
    Blocking loop — listens -> generates -> speaks until stop_event is set.
    Use as a thread target.
    """
    print(f"[assistant] Starting assistant ({language})")
    voice_id = voice_map.get(language,"en-IN-eashwar")
    while True:
        if stop_event and stop_event.is_set():
            print(f"[assistant] Stop requested for {language}")
            break
        user_text = listen(language)
        if not user_text:
            time.sleep(0.5)
            continue
        print(f"[assistant] Heard ({language}): {user_text}")
        prompt = f"Reply in {language} as a friendly helpful assistant, understandable for elderly people: {user_text}"
        raw_answer = ask_gemini(prompt)
        final_answer = translate_if_needed(raw_answer, language)
        print(f"[assistant] Response: {final_answer}")
        speak_murf_live(final_answer, voice_id)
        time.sleep(0.3)
    print(f"[assistant] Exiting assistant ({language})")
