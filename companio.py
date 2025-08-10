import os
import io
import time
import requests
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from openai import OpenAI
from murf import Murf
from deep_translator import GoogleTranslator

# ------------------ CONFIG ------------------
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)
murf_client = Murf(api_key="ap2_353f83f1-51b5-421e-b57d-5a817941e293")

voice_map = {
    "English": "en-IN-eashwar",
    "Tamil": "ta-IN-iniya",
    "Hindi": "hi-IN-priya"
}

lang_code_map = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi"
}

# ------------------ FUNCTIONS ------------------
def listen(language="English"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"🎤 Listening ({language})... (CTRL+C to quit)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=8)

    try:
        if language == "Tamil":
            return recognizer.recognize_google(audio, language="ta-IN")
        elif language == "Hindi":
            return recognizer.recognize_google(audio, language="hi-IN")
        else:
            return recognizer.recognize_google(audio, language="en-IN")
    except Exception as e:
        print("[STT Error]", e)
        return None

def ask_gemini(prompt):
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://companio.ai",
                "X-Title": "CompanioBot"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR] {e}"

def speak_murf_live(text, voice_id):
    try:
        resp = murf_client.text_to_speech.generate(
            text=text,
            voice_id=voice_id,
            format="WAV"
        )
        audio_url = resp.audio_file
        audio_data = requests.get(audio_url).content
        audio_buf = io.BytesIO(audio_data)
        seg = AudioSegment.from_file(audio_buf, format="wav")
        play(seg)
    except Exception as e:
        print("[TTS Error]", e)

def translate_if_needed(text, language):
    lang_code = lang_code_map.get(language, "en")
    if lang_code == "en":
        return text
    return GoogleTranslator(source='auto', target=lang_code).translate(text)

# ------------------ MAIN KEEP-ALIVE LOOP ------------------
if __name__ == "__main__":
    print("🤖 Companio Voice Assistant (English / Tamil / Hindi)")
    language = input("Select language: English / Tamil / Hindi: ").strip().title()

    try:
        while True:  # Keep-alive outer loop
            try:
                user_text = listen(language)
                if not user_text:
                    time.sleep(1)
                    continue

                print(f"🗣 You said ({language}): {user_text}")

                prompt = f"Reply in {language} as a friendly helpful assistant, understandable for elderly people: {user_text}"
                raw_answer = ask_gemini(prompt)
                final_answer = translate_if_needed(raw_answer, language)

                print(f"🤖 Companio: {final_answer}")
                speak_murf_live(final_answer, voice_map[language])

            except Exception as e:
                print("[Loop Error]", e)
                time.sleep(1)  # Wait before retry

    except KeyboardInterrupt:
        print("\n👋 Session ended by user.")
