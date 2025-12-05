from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! 🚀"

def run():
    # Render assigns a port via environment variable, default to 8080
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run, daemon=True)  # <--- This fixes the Ctrl+C issue
    t.start()