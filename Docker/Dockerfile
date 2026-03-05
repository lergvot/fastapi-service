# Docker/Dockerfile
FROM python:3.13-slim AS builder

# Устанавливаем зависимости для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.13-slim

# Копируем установленные зависимости из builder-стадии
COPY --from=builder /root/.local /root/.local

# Устанавливаем только runtime-зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Обновляем PATH для локальных пакетов
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . .

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]