# Зуброслов

Приложение для изучения английских слов с отслеживанием прогресса.

## Локальная разработка с Colima

Для локальной разработки без Docker Desktop можно использовать Colima:

### Установка Colima

```bash
# Установка через Homebrew
brew install colima docker docker-compose
```

### Запуск Colima

```bash
# Запуск с настройками по умолчанию
colima start

# Или с пользовательскими настройками ресурсов
colima start --cpu 2 --memory 4 --disk 10
```

### Проверка установки

```bash
# Проверка работы Docker
docker ps

# Проверка версии Docker Compose
docker-compose --version
```

### Запуск приложения

Для локальной разработки используется файл `docker-compose.override.yml`, который автоматически применяется вместе с основным `docker-compose.yml`. Это позволяет иметь разные настройки для разработки и продакшена.

```bash
# Запуск контейнеров
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка контейнеров
docker-compose down
```

### Фронтенд

Для локальной разработки фронтенда:

```bash
cd frontend
npm install
npm run dev
```

## Настройка PostgreSQL для продакшена

Для продакшена используется PostgreSQL в Yandex Cloud. Для настройки соединения с SSL:

### 1. Скачать SSL-сертификат

```bash
# На продакшен-сервере
mkdir -p /home/ubuntu/zubroslov/certs
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
     --output-document /home/ubuntu/zubroslov/certs/root.crt
chmod 0655 /home/ubuntu/zubroslov/certs/root.crt
```

### 2. Настроить .env файл

Создайте файл `/home/ubuntu/zubroslov/.env` с настройками подключения:

```
DATABASE_URL=postgresql://dbadmin:your_password@c-c9qqpa50hhvmpoidilk4.rw.mdb.yandexcloud.net:6432/main?sslmode=verify-full
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Обновить deploy.sh

Файл `deploy.sh` должен монтировать директорию с сертификатом:

```bash
docker run -d --name zubroslov-api \
  -p 8000:8000 \
  -v /home/ubuntu/zubroslov/.env:/app/.env \
  -v static_volume:/app/static \
  -v /home/ubuntu/zubroslov/certs:/home/appuser/.postgresql \
  --restart unless-stopped \
  cr.yandex/crp5dp8t30l3r6brejfj/zubroslov-api:latest
```

### 4. Подготовка файла со словами

Создайте файл `all_words.json` в директории `/app` на сервере:

```bash
# Скопируйте файл all_words.json на сервер
scp scripts/all_words.json user@your-server:/home/ubuntu/zubroslov/all_words.json

# Скопируйте файл в контейнер
docker cp /home/ubuntu/zubroslov/all_words.json zubroslov-api:/app/all_words.json
```

### 5. Импорт слов

После настройки PostgreSQL и подготовки файла со словами, импортируйте слова:

```bash
./import_words_to_postgres.sh
```

## Деплой

Деплой осуществляется автоматически через GitHub Actions при пуше в ветку main:

- Фронтенд деплоится в Yandex Object Storage
- Бэкенд деплоится в Docker контейнере на виртуальной машине в Yandex Cloud

## Структура проекта

- `backend/` - FastAPI приложение
- `frontend/` - React приложение
- `scripts/` - Скрипты для импорта слов и генерации аудио
- `infrastructure/` - Конфигурация инфраструктуры (API Gateway и т.д.)
