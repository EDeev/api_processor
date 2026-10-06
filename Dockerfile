FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DB_PATH=/data/db.sqlite3 \
    DJANGO_MEDIA_ROOT=/data/media \
    VOSK_MODEL_PATH=/app/models/vosk-model-small-ru-0.22

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# офлайн-модель распознавания русской речи (~45 МБ)
RUN mkdir -p models \
    && curl -fsSL -o /tmp/model.zip https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip \
    && unzip -q /tmp/model.zip -d models \
    && rm /tmp/model.zip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py ./
COPY api_project/ api_project/
COPY api_app/ api_app/
COPY proto/ proto/

RUN useradd --create-home --uid 1000 app && mkdir -p /data && chown -R app:app /app /data
USER app
VOLUME ["/data"]
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn api_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 300"]
