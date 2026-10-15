#!/usr/bin/env bash
# Прекратить выполнение при любой ошибке
set -o errexit

# 1. Обновляем pip и устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# 2. Собираем статические файлы (CSS, JS, картинки шаблонов)
python manage.py collectstatic --no-input

# 3. Применяем миграции базы данных
python manage.py migrate