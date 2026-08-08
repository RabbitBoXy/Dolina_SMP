from flask import Flask, jsonify
from flask_cors import CORS
from mcstatus import JavaServer
import time
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)  # разрешаем запросы с любого сайта

# Настройки твоего сервера
SERVER_HOST = "d2.rustix.me"
SERVER_PORT = 25172

# Кеш для статуса (чтобы не дёргать сервер при каждом запросе)
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
    """Фоновый процесс, который обновляет статус каждые 30 секунд"""
    global cached_status
    while True:
        try:
            print(f"🔄 Проверяю сервер {SERVER_HOST}:{SERVER_PORT}...")
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
        
        time.sleep(30)  # пауза 30 секунд

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Minecraft server status API",
        "endpoints": {
            "/status": "Получить статус сервера"
        }
    })

@app.route('/status')
def get_status():
    """Возвращает текущий статус сервера"""
    return jsonify(cached_status)

if __name__ == '__main__':
    # Запускаем фоновый поток для обновления статуса
    thread = threading.Thread(target=update_status_loop, daemon=True)
    thread.start()
    print("🚀 Сервер запущен на порту 10000")
    app.run(host='0.0.0.0', port=10000)
