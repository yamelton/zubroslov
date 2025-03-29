# Базовый образ Python 3.10
FROM python:3.10-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости ПЕРВЫМИ
COPY requirements.txt .

# Установка системных зависимостей для PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt -v

# Копируем остальные файлы
COPY . .
RUN pip install -e .

RUN mkdir -p /app/static && chmod -R 755 /app/static

# Создаем непривилегированного пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Переменные окружения
ENV PYTHONPATH=/app
ENV DB_URL=postgresql+asyncpg://user:pass@host/dbname

# Команда запуска
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
