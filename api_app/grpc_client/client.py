import logging
import os
import sys

import grpc
from django.conf import settings

# сгенерированные модули лежат в proto/ в корне репозитория (раньше путь считался на уровень
# выше репозитория — импорт всегда падал, и вместо настоящего gRPC работала заглушка
# с поддельным success: true)
PROTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "proto")
if PROTO_DIR not in sys.path:
    sys.path.append(PROTO_DIR)

import text_service_pb2  # noqa: E402
import text_service_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)


def send_to_grpc_server(text: str):
    """Отправляет текст на gRPC-сервер TextProcessor. Если адрес сервера не задан
    (GRPC_SERVER пустой), шаг пропускается и возвращается None"""
    if not settings.GRPC_SERVER:
        return None

    try:
        with grpc.insecure_channel(settings.GRPC_SERVER) as channel:
            stub = text_service_pb2_grpc.TextProcessorStub(channel)
            response = stub.ProcessText(text_service_pb2.TextRequest(text=text), timeout=settings.GRPC_TIMEOUT)
        return {
            'processed_text': response.processed_text,
            'success': response.success,
            'error': response.error or None,
        }
    except grpc.RpcError as e:
        logger.warning("gRPC-сервер %s недоступен: %s", settings.GRPC_SERVER, e.code())
        return {'processed_text': None, 'success': False, 'error': f"gRPC: {e.code().name}"}
