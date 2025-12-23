# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаем директории для данных и кэша
RUN mkdir -p data cache

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data
ENV PORT=8000

# Открываем порт (Railway автоматически установит PORT)
EXPOSE $PORT

# Команда запуска (Railway использует переменную PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

