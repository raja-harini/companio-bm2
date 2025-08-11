import os, threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()
from companio_core import run_assistant

CONTROL_API_KEY = os.getenv("CONTROL_API_KEY","changeme")
app = Flask("companio-server")

threads = {}    # lang -> Thread
events = {}     # lang -> Event

def auth_ok(req):
    token = req.headers.get("X-API-KEY") or req.args.get("key")
    return token == CONTROL_API_KEY

@app.route("/start/<lang>", methods=["POST"])
def start_lang(lang):
    if not auth_ok(request):
        return jsonify({"error":"unauthorized"}), 401
    lang = lang.title()
    if lang in threads and threads[lang].is_alive():
        return jsonify({"status":"already_running","lang":lang})
    evt = threading.Event()
    th = threading.Thread(target=run_assistant, args=(lang, evt), daemon=True)
    threads[lang] = th
    events[lang] = evt
    th.start()
    return jsonify({"status":"started","lang":lang})

@app.route("/stop/<lang>", methods=["POST"])
def stop_lang(lang):
    if not auth_ok(request):
        return jsonify({"error":"unauthorized"}), 401
    lang = lang.title()
    if lang not in events:
        return jsonify({"status":"not_running","lang":lang})
    events[lang].set()
    return jsonify({"status":"stopping","lang":lang})

@app.route("/status", methods=["GET"])
def status():
    if not auth_ok(request):
        return jsonify({"error":"unauthorized"}), 401
    out = {lang: (threads[lang].is_alive() if lang in threads else False) for lang in ["English","Tamil","Hindi"]}
    return jsonify(out)


# ======== Health Monitor Integration Starts Here ========

from health_monitor_core import HealthMonitorRunner

health_runner = HealthMonitorRunner()

@app.route('/health_monitor/start', methods=['POST'])
def start_health_monitor():
    if not auth_ok(request):
        return jsonify({"error":"unauthorized"}), 401
    data = request.json
    language = data.get('language')
    if not language:
        return jsonify({"status":"error","message":"language not specified"}), 400
    try:
        health_runner.start(language)
        return jsonify({"status": "started", "language": language})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health_monitor/stop', methods=['POST'])
def stop_health_monitor():
    if not auth_ok(request):
        return jsonify({"error":"unauthorized"}), 401
    health_runner.stop()
    return jsonify({"status": "stopped"})

# ======== Health Monitor Integration Ends Here ========


if __name__ == "__main__":
    # Run on localhost:5000 (loopback) — ok for adb reverse
    app.run(host="127.0.0.1", port=5000, debug=False)
