import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот запущен и работает!"

def run():
    # Получаем порт из переменной окружения (например, Render передаёт его через PORT)
    port = int(os.environ.get("PORT", 5000))
    # Запускаем Flask с отключённым режимом отладки и автоматическим перезапуском
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)