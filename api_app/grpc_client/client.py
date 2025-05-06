# api_project/api_app/grpc_client/client.py
import grpc
import os
import sys

# Добавляем путь для импорта сгенерированных протофайлов
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 'proto')
sys.path.append(proto_dir)

# Пробуем импортировать сгенерированные протофайлы
# Если не получится, используем заглушки
try:
    import text_service_pb2
    import text_service_pb2_grpc
    print("Успешно импортированы сгенерированные proto файлы")
except ImportError:
    print("Не удалось импортировать сгенерированные proto файлы, используем заглушки")
    
    # Создаем заглушки
    class TextRequest:
        def __init__(self, text):
            self.text = text
    
    class TextResponse:
        def __init__(self, processed_text, success, error):
            self.processed_text = processed_text
            self.success = success
            self.error = error
    
    class TextProcessorStub:
        def __init__(self, channel):
            self.channel = channel
        
        def ProcessText(self, request):
            # Эмулируем ответ от gRPC сервера
            return TextResponse(
                processed_text=f"ЗАГЛУШКА ОБРАБОТКИ ТЕКСТА: {request.text}",
                success=True,
                error=""
            )
    
    # Создаем модуль заглушки
    class text_service_pb2:
        TextRequest = TextRequest
        TextResponse = TextResponse
    
    class text_service_pb2_grpc:
        TextProcessorStub = TextProcessorStub

def send_to_grpc_server(text: str) -> dict:
    """
    Отправляет текст на gRPC сервер для обработки
    
    Args:
        text: Текст для обработки
        
    Returns:
        dict: Результат обработки
    """
    try:
        # Создаем соединение с сервером
        # Для заглушки это не обязательно, но оставим для совместимости
        try:
            channel = grpc.insecure_channel('localhost:50051')
        except NameError:
            # Если grpc не импортирован, используем заглушку
            channel = "dummy_channel"
        
        # Создаем клиент
        stub = text_service_pb2_grpc.TextProcessorStub(channel)
        
        # Создаем запрос
        request = text_service_pb2.TextRequest(text=text)
        
        # Отправляем запрос
        response = stub.ProcessText(request)
        
        # Возвращаем результат
        return {
            'processed_text': response.processed_text,
            'success': response.success,
            'error': response.error if hasattr(response, 'error') and response.error else None
        }
    except Exception as e:
        return {
            'processed_text': None,
            'success': False,
            'error': str(e)
        }
