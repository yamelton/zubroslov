#!/bin/bash
set -e

# Логирование для отладки
exec > >(tee -a /home/ubuntu/zubroslov/logs/deploy.log) 2>&1
echo "[$(date)] Начинаем обновление контейнера zubroslov-api"

# Создаем директорию для логов, если её нет
mkdir -p /home/ubuntu/zubroslov/logs

# Проверка наличия и остановка существующего контейнера
if docker ps -a | grep -q zubroslov-api; then
  echo "[$(date)] Останавливаем существующий контейнер"
  docker stop zubroslov-api || true
  docker rm zubroslov-api || true
fi

# Проверка наличия и остановка отладочного контейнера
if docker ps -a | grep -q zubroslov-api-debug; then
  echo "[$(date)] Останавливаем отладочный контейнер"
  docker stop zubroslov-api-debug || true
  docker rm zubroslov-api-debug || true
fi

# Настройка Docker для работы с Container Registry
echo "[$(date)] Настройка Docker для работы с Container Registry"
export PATH=$PATH:/home/ubuntu/yandex-cloud/bin
yc container registry configure-docker

# Получение последнего образа
echo "[$(date)] Получаем последний образ из Container Registry"
docker pull cr.yandex/crp5dp8t30l3r6brejfj/zubroslov-api:latest

# Запуск нового контейнера
echo "[$(date)] Запускаем новый контейнер"
docker run -d --name zubroslov-api \
  -p 8000:8000 \
  -v /home/ubuntu/zubroslov/.env:/app/.env \
  -v static_volume:/app/static \
  --restart unless-stopped \
  cr.yandex/crp5dp8t30l3r6brejfj/zubroslov-api:latest

# Ждем 10 секунд для запуска контейнера
echo "[$(date)] Ждем запуска контейнера..."
sleep 10

# Проверяем, что API отвечает
if curl -s http://localhost:8000/ | grep -q "Welcome"; then
  echo "[$(date)] API успешно запущен"
else
  echo "[$(date)] ПРЕДУПРЕЖДЕНИЕ: API не отвечает на запрос к корневому пути"
  # Проверяем, запущен ли контейнер
  if docker ps | grep -q zubroslov-api; then
    echo "[$(date)] Контейнер запущен, но API не отвечает. Проверьте логи контейнера."
  else
    echo "[$(date)] ОШИБКА: Контейнер не запущен"
    exit 1
  fi
fi

echo "[$(date)] Обновление завершено успешно"
