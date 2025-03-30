# Тестовое окружение Zubroslov

Этот документ описывает настройку и использование тестового окружения для проекта Zubroslov.

## Структура окружений

### Домены
- **Продакшн**: zubroslov.ru
- **Тест**: test.zubroslov.ru

### API
- **Продакшн**: api.zubroslov.ru
- **Тест**: api-test.zubroslov.ru

### Базы данных
- **Продакшн**: main
- **Тест**: test

### Статические файлы
- **Продакшн**: /var/www/static/
- **Тест**: /var/www/test-static/

### Docker контейнеры
- **Продакшн**: zubroslov-api
- **Тест**: zubroslov-api-test

### Object Storage
- **Продакшн**: бакет zubroslov.ru
- **Тест**: бакет test.zubroslov.ru

## Настройка тестового окружения

### 1. Настройка DNS
Создайте A-записи для доменов `test.zubroslov.ru` и `api-test.zubroslov.ru`, указывающие на IP-адрес вашего сервера.

### 2. Настройка SSL-сертификатов
Получите SSL-сертификаты для тестовых доменов с помощью Certbot:

```bash
sudo certbot certonly --nginx -d test.zubroslov.ru
sudo certbot certonly --nginx -d api-test.zubroslov.ru
```

### 3. Настройка Nginx
Скопируйте конфигурационные файлы из директории `infrastructure/nginx/` в `/etc/nginx/sites-available/` и создайте символические ссылки в `/etc/nginx/sites-enabled/`:

```bash
sudo cp infrastructure/nginx/test.zubroslov.ru /etc/nginx/sites-available/
sudo cp infrastructure/nginx/api-test.zubroslov.ru /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/test.zubroslov.ru /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api-test.zubroslov.ru /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Создание директорий для статических файлов
```bash
sudo mkdir -p /var/www/test-static/audio
sudo chown -R $USER:$USER /var/www/test-static
```

### 5. Создание тестовой базы данных
```bash
psql -U postgres -c "CREATE DATABASE test;"
```

### 6. Настройка GitHub Actions
Для автоматического деплоя в тестовое окружение используются следующие GitHub Actions:
- `.github/workflows/deploy-template.yml` - шаблон для деплоя
- `.github/workflows/deploy-prod.yml` - деплой в продакшн
- `.github/workflows/deploy-test.yml` - деплой в тестовое окружение

Необходимые секреты в GitHub:
- `SERVER_HOST`: хост сервера
- `SERVER_USERNAME`: имя пользователя для SSH-подключения
- `SSH_KEY`: приватный ключ для SSH-подключения
- `YC_STORAGE_ACCESS_KEY`: ключ доступа к Object Storage
- `YC_STORAGE_SECRET_KEY`: секретный ключ для Object Storage
- `YC_SERVICE_ACCOUNT_KEY`: ключ сервисного аккаунта Yandex Cloud
- `YC_REGISTRY_ID`: ID Container Registry

## Использование тестового окружения

### Деплой в тестовое окружение
```bash
./deploy.sh --env test
```

### Импорт слов в тестовую базу данных
```bash
./import_words_to_test.sh
```

### Просмотр логов тестового окружения
```bash
docker logs -f zubroslov-api-test
```

## Процесс разработки с использованием тестового окружения

1. Разработка ведется в ветке `develop`
2. При пуше в ветку `develop` автоматически запускается деплой в тестовое окружение через GitHub Actions
3. Тестирование проводится на домене `test.zubroslov.ru`
4. После успешного тестирования создается релиз, который автоматически деплоится в продакшн

## Различия между окружениями

- Тестовое окружение использует отдельную базу данных
- Тестовое окружение использует отдельную директорию для статических файлов
- Тестовое окружение работает на отдельном порту (8001 для API)
- Тестовое окружение использует отдельный Docker контейнер для бэкенда
- Фронтенд для обоих окружений размещается в Object Storage (разные бакеты)
