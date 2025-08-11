# health_monitor_core.py

import subprocess
import threading
import os
import signal
import sys

# Map languages to python script filenames
LANG_TO_SCRIPT = {
    "English": "hmeng.py",
    "Tamil": "hmtam.py",
    "Hindi": "hmhin.py"
}

class HealthMonitorRunner:
    def __init__(self):
        self.process = None

    def start(self, language):
        if language not in LANG_TO_SCRIPT:
            raise ValueError(f"Unsupported language: {language}")
        script = LANG_TO_SCRIPT[language]
        # Stop any running process
        self.stop()

        # Run the python script in a subprocess
        self.process = subprocess.Popen(
            [sys.executable, script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Start thread to read stdout and print logs (optional)
        threading.Thread(target=self._read_stdout, daemon=True).start()

    def _read_stdout(self):
        if not self.process:
            return
        for line in self.process.stdout:
            print(f"[HealthMonitor] {line.strip()}")

    def stop(self):
        if self.process and self.process.poll() is None:
            # Terminate the process gracefully
            if os.name == 'nt':  # Windows
                self.process.terminate()
            else:  # Unix
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()
            print("[HealthMonitor] Process stopped")
            self.process = None

if __name__ == "__main__":
    # For quick manual test
    runner = HealthMonitorRunner()
    runner.start("English")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        runner.stop()
