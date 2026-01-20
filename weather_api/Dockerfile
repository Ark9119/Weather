FROM python:3.12-slim

WORKDIR /app

RUN pip install gunicorn==23.0.0 

COPY requirements.txt .

RUN pip install gunicorn==23.0.0 && \
    pip install -r requirements.txt --no-cache-dir

# Установка curl и bash
RUN apt-get update && \
    apt-get install -y curl bash && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Открываем порт 8001
EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "weather_api.wsgi:application"]