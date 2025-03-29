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

## Деплой

Деплой осуществляется автоматически через GitHub Actions при пуше в ветку main:

- Фронтенд деплоится в Yandex Object Storage
- Бэкенд деплоится в Docker контейнере на виртуальной машине в Yandex Cloud

## Структура проекта

- `backend/` - FastAPI приложение
- `frontend/` - React приложение
- `scripts/` - Скрипты для импорта слов и генерации аудио
- `infrastructure/` - Конфигурация инфраструктуры (API Gateway и т.д.)
