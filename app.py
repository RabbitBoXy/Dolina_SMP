from flask import Flask, jsonify
from flask_cors import CORS
from mcstatus import JavaServer
from datetime import datetime
import time
import threading

app = Flask(__name__)
CORS(app)

# Глобальный кеш
cached_status = {"online": False, "players": 0}

def update_status():
    global cached_status
    while True:
        try:
            server = JavaServer.lookup("d2.rustix.me:25172")
            status = server.status()
            cached_status = {
                "online": True,
                "players": status.players.online,
                "max_players": status.players.max,
                "version": status.version.name,
                "motd": str(status.description),
                "latency": round(status.latency, 2),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"✅ Сервер работает, игроков: {status.players.online}")
        except Exception as e:
            cached_status = {
                "online": False,
                "players": 0,
                "max_players": 0,
                "version": "Неизвестно",
                "motd": "",
                "latency": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }
            print(f"❌ Ошибка: {e}")
        time.sleep(30)

# Запускаем поток
thread = threading.Thread(target=update_status, daemon=True)
thread.start()

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Minecraft API"})

@app.route('/status')
def status():
    return jsonify(cached_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
