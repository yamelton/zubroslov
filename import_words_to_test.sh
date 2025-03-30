#!/bin/bash
set -e

# Директория проекта
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Импорт слов в тестовую базу данных..."

# Проверка наличия тестового контейнера
if ! docker ps | grep -q zubroslov-api-test; then
  echo "Ошибка: Тестовый контейнер zubroslov-api-test не запущен."
  echo "Сначала запустите тестовое окружение: ./deploy.sh --env test"
  exit 1
fi

# Запуск скрипта импорта слов в тестовом контейнере
docker exec -it zubroslov-api-test python -m scripts.import_words --env test

echo "Импорт завершен."
