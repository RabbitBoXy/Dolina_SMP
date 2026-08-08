from flask import Flask, jsonify
from flask_cors import CORS
from mcstatus import JavaServer
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Настройки твоего сервера
SERVER_HOST = "d2.rustix.me"
SERVER_PORT = 25172

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
    """Фоновый поток обновления статуса через mcstatus"""
    global cached_status
    while True:
        try:
            print(f"🔄 Проверяю {SERVER_HOST}:{SERVER_PORT} через mcstatus...")
            
            # Пытаемся подключиться к серверу
            server = JavaServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
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
            print(f"❌ Ошибка mcstatus: {e}")
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
        
        time.sleep(30)

# Запускаем фоновый поток
thread = threading.Thread(target=update_status_loop, daemon=True)
thread.start()
print("🚀 Фоновый поток обновления статуса запущен")

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
    app.run(host='0.0.0.0', port=10000)
