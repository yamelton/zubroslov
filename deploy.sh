#!/bin/bash
set -e

# Default values
ENV="prod"
API_CONTAINER_NAME="zubroslov-api"
API_PORT="8000"
ENV_FILE=".env"
STATIC_VOLUME="static_volume"
IMAGE_TAG="latest"
LOG_FILE="deploy.log"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --env)
      ENV="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set environment-specific values
if [[ "$ENV" == "test" ]]; then
  API_CONTAINER_NAME="zubroslov-api-test"
  API_PORT="8001"
  ENV_FILE=".env.test"
  STATIC_VOLUME="/var/www/test-static"
  IMAGE_TAG="test"
  LOG_FILE="deploy-test.log"
fi

# Логирование для отладки
exec > >(tee -a /home/ubuntu/zubroslov/logs/$LOG_FILE) 2>&1
echo "[$(date)] Начинаем обновление контейнера $API_CONTAINER_NAME (окружение: $ENV)"

# Создаем директорию для логов, если её нет
mkdir -p /home/ubuntu/zubroslov/logs

# Проверка наличия и остановка существующего API контейнера
if docker ps -a | grep -q $API_CONTAINER_NAME; then
  echo "[$(date)] Останавливаем существующий API контейнер"
  docker stop $API_CONTAINER_NAME || true
  docker rm $API_CONTAINER_NAME || true
fi

# Настройка Docker для работы с Container Registry
echo "[$(date)] Настройка Docker для работы с Container Registry"
export PATH=$PATH:/home/ubuntu/yandex-cloud/bin
yc container registry configure-docker

# Получение последнего образа
echo "[$(date)] Получаем последний образ из Container Registry"
docker pull cr.yandex/crp5dp8t30l3r6brejfj/zubroslov-api:$IMAGE_TAG

# Создаем директорию для статических файлов, если это тестовое окружение
if [[ "$ENV" == "test" ]]; then
  mkdir -p /var/www/test-static
fi

# Запуск нового API контейнера
echo "[$(date)] Запускаем новый API контейнер"
docker run -d --name $API_CONTAINER_NAME \
  -p $API_PORT:8000 \
  -v /home/ubuntu/zubroslov/$ENV_FILE:/app/.env \
  -v $STATIC_VOLUME:/app/static \
  -v /home/ubuntu/zubroslov/certs:/home/appuser/.postgresql \
  -e ENV=$ENV \
  --restart unless-stopped \
  cr.yandex/crp5dp8t30l3r6brejfj/zubroslov-api:$IMAGE_TAG

# Ждем 10 секунд для запуска контейнера
echo "[$(date)] Ждем запуска контейнера..."
sleep 10

# Проверяем, что API отвечает
if curl -s http://localhost:$API_PORT/ | grep -q "Welcome"; then
  echo "[$(date)] API успешно запущен"
else
  echo "[$(date)] ПРЕДУПРЕЖДЕНИЕ: API не отвечает на запрос к корневому пути"
  # Проверяем, запущен ли контейнер
  if docker ps | grep -q $API_CONTAINER_NAME; then
    echo "[$(date)] Контейнер запущен, но API не отвечает. Проверьте логи контейнера."
  else
    echo "[$(date)] ОШИБКА: Контейнер не запущен"
    exit 1
  fi
fi

echo "[$(date)] Обновление окружения $ENV завершено успешно"
