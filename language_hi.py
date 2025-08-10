# language_hi.py
import threading
from companio_core import run_assistant
if __name__ == "__main__":
    stop_evt = threading.Event()
    try:
        run_assistant("Hindi", stop_evt)
    except KeyboardInterrupt:
        stop_evt.set()