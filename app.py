from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

cached_status = {
    "online": False,
    "players": 0,
    "max_players": 0,
    "version": "Неизвестно",
    "motd": "",
    "latency": 0,
    "last_updated": "Запуск..."
}

def update_status_loop():
    global cached_status
    while True:
        try:
            # Используем API mcsrvstat.us (он видит твой сервер)
            resp = requests.get(
                'https://api.mcsrvstat.us/2/d2.rustix.me',
                timeout=10
            )
            data = resp.json()
            
            online = data.get('online', False)
            
            cached_status = {
                "online": online,
                "players": data.get('players', {}).get('online', 0) if online else 0,
                "max_players": data.get('players', {}).get('max', 0) if online else 0,
                "version": data.get('version', 'Неизвестно') if online else 'Неизвестно',
                "motd": str(data.get('motd', {}).get('clean', [''])[0]) if online else '',
                "latency": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"✅ Статус: {'онлайн' if online else 'офлайн'}, игроков: {cached_status['players']}")
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

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Minecraft server status API",
        "endpoint": "/status"
    })

@app.route('/status')
def get_status():
    return jsonify(cached_status)

if __name__ == '__main__':
    thread = threading.Thread(target=update_status_loop, daemon=True)
    thread.start()
    print("🚀 Сервер запущен")
    app.run(host='0.0.0.0', port=10000)
