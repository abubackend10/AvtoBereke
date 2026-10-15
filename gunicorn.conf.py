import os
import multiprocessing

# Прослушивание через Unix-сокет (рекомендуется для связки с Nginx) или порт
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"
# Если захотите запустить через порт: bind = "127.0.0.1:8000"

# Количество воркеров (по формуле: 2 * ядра + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Количество потоков на один воркер
threads = 2

# Таймаут для долгих запросов (в секундах)
timeout = 60

# Логирование
accesslog = "-"
errorlog = "-"

# Перехват стандартного вывода в лог ошибок
capture_output = True