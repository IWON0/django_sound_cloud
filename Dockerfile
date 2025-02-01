FROM python:3.9.9

# Установка рабочего каталога
WORKDIR /usr/src/app

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка необходимых системных пакетов и postgresql-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    ntp \
    tzdata \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip до стабильной версии
RUN pip install --no-cache-dir --upgrade pip==23.3.1

# Копирование зависимостей и установка Python-пакетов
COPY ./requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя non-root
RUN useradd -m appuser && chown -R appuser /usr/src/app
USER appuser

# Копирование исходных файлов проекта
COPY . /usr/src/app/
