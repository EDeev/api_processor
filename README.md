# API Processor

**Django REST API для обработки аудио и документов с интеграцией gRPC сервисов**

API Processor — это мощное решение для автоматической обработки мультимедийного контента. Система выполняет транскрибацию аудиофайлов в текст и извлечение данных из PDF/DOCX документов с последующей отправкой результатов на внешний gRPC сервер для дополнительной обработки.

## 🚀 Возможности

- **Аудио транскрипция**: Преобразование аудиофайлов в текст с использованием модели Vosk
- **Обработка документов**: Извлечение текста, таблиц и изображений из PDF и DOCX файлов
- **gRPC интеграция**: Автоматическая отправка обработанного текста на внешний сервер
- **RESTful API**: Простой и понятный интерфейс для взаимодействия
- **Поддержка форматов**: Audio (WAV, OGG и др.), PDF, DOCX

## 🛠 Технологический стек

### Backend
- **Django 4.2.6** - веб-фреймворк
- **Django REST Framework 3.14.0** - API framework
- **Python** - основной язык разработки

### Обработка контента
- **Vosk 0.3.45** - распознавание речи
- **FFmpeg Python 0.2.0** - конвертация аудио
- **pdfplumber 0.10.2** - извлечение данных из PDF
- **python-docx 0.8.11** - работа с DOCX файлами
- **Pillow 10.0.1** - обработка изображений

### Коммуникация
- **gRPC 1.58.0** - межсервисное взаимодействие
- **Protocol Buffers** - сериализация данных

### База данных
- **SQLite** - локальное хранение метаданных файлов

## 📋 Требования

- Python 3.8+
- FFmpeg (для конвертации аудио)
- Модель Vosk для русского языка

## ⚡ Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка модели Vosk

1. Скачайте модель `vosk-model-small-ru-0.22`
2. Разместите в папке `models/vosk-model-small-ru-0.22`

### Настройка FFmpeg

1. Скачайте FFmpeg
2. Разместите в `models/ffmpeg/bin/ffmpeg.exe`

### Запуск сервера

```bash
python manage.py migrate
python manage.py runserver
```

## 📖 API Endpoints

### Транскрипция аудио
```http
POST /api/audio-to-text/
Content-Type: multipart/form-data

audio: <audio_file>
```

**Ответ:**
```json
{
    "text": "Распознанный текст из аудио",
    "grpc_response": {
        "processed_text": "Обработанный текст",
        "success": true,
        "error": null
    }
}
```

### Обработка документов
```http
POST /api/document-to-text/
Content-Type: multipart/form-data

document: <pdf_or_docx_file>
```

**Ответ:**
```json
{
    "text": "<p>Извлеченный текст</p><pre>таблица,данные</pre>",
    "grpc_response": {
        "processed_text": "Обработанный текст",
        "success": true,
        "error": null
    }
}
```

## 🧪 Примеры использования

### cURL команды

**Транскрипция аудио:**
```bash
curl -X POST -F "audio=@audio.ogg" http://localhost:8000/api/audio-to-text/
```

**Обработка документа:**
```bash
curl -X POST -F "document=@document.pdf" http://localhost:8000/api/document-to-text/
```

## ⚙️ Конфигурация

### gRPC настройки
По умолчанию система подключается к gRPC серверу на `localhost:50051`. Для изменения адреса отредактируйте `api_app/grpc_client/client.py`.

### Модели и пути
Пути к моделям и исполняемым файлам настраиваются в `api_app/services/vosk_recognizer.py`:
- `MODEL_PATH` - путь к модели Vosk
- `FFMPEG_PATH` - путь к исполняемому файлу FFmpeg

## 📁 Структура проекта

```
api_processor/
├── api_app/                    # Основное приложение
│   ├── grpc_client/           # gRPC клиент
│   ├── services/              # Сервисы обработки
│   ├── migrations/            # Миграции БД
│   ├── models.py              # Модели данных
│   └── views.py               # API эндпоинты
├── api_project/               # Настройки Django
├── proto/                     # Protocol Buffers схемы
├── models/                    # Модели и исполняемые файлы
└── requirements.txt           # Зависимости
```

## 🔧 Особенности реализации

- **Автоматическая конвертация**: Аудиофайлы автоматически конвертируются в формат WAV 16kHz
- **Извлечение изображений**: Из документов извлекаются изображения в формате base64
- **Обработка таблиц**: Таблицы сохраняются в CSV формате
- **Fallback система**: При недоступности gRPC сервера используются заглушки

## 📄 Лицензия

Этот проект разработан для образовательных и исследовательских целей.

## 🤝 Разработчик

**Деев Егор Викторович** - Backend Developer  
- GitHub: [@EDeev](https://github.com/EDeev)
- Email: egor@deev.space
- Telegram: [@Egor_Deev](https://t.me/Egor_Deev)

---

<div align="center">
  <p><sub>Создано с ❤️ от вашего дорогого - deev.space ©</sub></p>
</div>
