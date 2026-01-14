import time
from flask import Flask
from threading import Thread
from runner.bot_loop import run_cycle
from config.settings import WATCHLIST, SCAN_INTERVAL_SEC

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def bot():
    while True:
        run_cycle(WATCHLIST)
        time.sleep(SCAN_INTERVAL_SEC)

if __name__ == "__main__":
    Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=3000)