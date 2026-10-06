import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")


DEBUG = env_bool("DJANGO_DEBUG")

# Ключ по умолчанию — только для разработки (DJANGO_DEBUG=True)
DEV_SECRET_KEY = "django-insecure-dev-only-change-me"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", DEV_SECRET_KEY if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("Задайте DJANGO_SECRET_KEY (или DJANGO_DEBUG=True для разработки)")

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Добавляем DRF
    'api_app',  # Наше API приложение
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get("DJANGO_DB_PATH", BASE_DIR / 'db.sqlite3'),
    }
}

# Путь для загрузки файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", os.path.join(BASE_DIR, 'media'))
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Распознавание и обработка
VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", BASE_DIR / "models" / "vosk-model-small-ru-0.22")
FFMPEG_BINARY = os.environ.get("FFMPEG_BINARY", "ffmpeg")  # из PATH; раньше — Windows-путь к ffmpeg.exe
GRPC_SERVER = os.environ.get("GRPC_SERVER", "localhost:50051")  # пусто — не отправлять на gRPC
GRPC_TIMEOUT = float(os.environ.get("GRPC_TIMEOUT", "10"))
API_TOKEN = os.environ.get("API_TOKEN", "")  # если задан — нужен заголовок Authorization: Bearer
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # крупные файлы — во временный файл, не в память

# Настройки для REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'api_app.permissions.ApiTokenPermission',
    ]
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# как в существующей миграции — без новой миграции
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
