import logging
import os

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .grpc_client.client import send_to_grpc_server
from .models import AudioFile, DocumentFile
from .services.scan import extract_text_tables
from .services.vosk_recognizer import RecognitionError, recognize_speech

logger = logging.getLogger(__name__)


def too_large(uploaded):
    return uploaded.size > settings.MAX_UPLOAD_SIZE


def size_error():
    return Response({'error': f'Файл больше {settings.MAX_UPLOAD_SIZE // 1024 // 1024} МБ'},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class ProcessView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    field = ""
    model = None

    def process(self, path):
        raise NotImplementedError

    def handle(self, uploaded):
        record = self.model(file=uploaded)
        record.save()

        try:
            text = self.process(os.path.join(settings.MEDIA_ROOT, record.file.name))
        except RecognitionError as e:
            return Response({'error': str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception:
            # подробности — в лог, а не в ответ клиенту
            logger.exception("Ошибка обработки %s", record.file.name)
            return Response({'error': 'Не удалось обработать файл'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        record.processed_text = text
        record.save()

        return Response({'text': text, 'grpc_response': send_to_grpc_server(text)}, status=status.HTTP_200_OK)


class AudioToTextView(ProcessView):
    model = AudioFile

    def process(self, path):
        return recognize_speech(path)

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({'error': 'Нет аудио файла'}, status=status.HTTP_400_BAD_REQUEST)
        if too_large(audio_file):
            return size_error()

        return self.handle(audio_file)


class DocumentToTextView(ProcessView):
    model = DocumentFile

    def process(self, path):
        return extract_text_tables(path)

    def post(self, request, *args, **kwargs):
        document_file = request.FILES.get('document')

        if not document_file:
            return Response({'error': 'Нет документа'}, status=status.HTTP_400_BAD_REQUEST)

        file_ext = os.path.splitext(document_file.name)[1].lower()
        if file_ext not in ['.pdf', '.docx']:
            return Response({'error': 'Поддерживаются только PDF и DOCX файлы'},
                            status=status.HTTP_400_BAD_REQUEST)
        if too_large(document_file):
            return size_error()

        return self.handle(document_file)
