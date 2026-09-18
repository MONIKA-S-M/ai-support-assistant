import subprocess
import sys

print("Starting AI Support Ticket Assistant...")

api = subprocess.Popen([
    sys.executable,
    "-m",
    "uvicorn",
    "app.main:app",
    "--reload",
])

streamlit = subprocess.Popen([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "streamlit_app.py",
])

try:
    api.wait()
    streamlit.wait()
except KeyboardInterrupt:
    print("\nStopping application...")
    api.terminate()
    streamlit.terminate()