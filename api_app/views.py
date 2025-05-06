# api_project/api_app/views.py
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from .models import AudioFile, DocumentFile
from .services.vosk_recognizer import recognize_speech
from .services.scan import extract_text_tables
from .grpc_client.client import send_to_grpc_server

class AudioToTextView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get('audio')
        
        if not audio_file:
            return Response({'error': 'Нет аудио файла'}, status=status.HTTP_400_BAD_REQUEST)
        
        audio_model = AudioFile(file=audio_file)
        audio_model.save()
        
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, audio_model.file.name)
            
            text = recognize_speech(file_path)
            
            audio_model.processed_text = text
            audio_model.save()
            
            grpc_response = send_to_grpc_server(text)
            
            return Response({
                'text': text,
                'grpc_response': grpc_response
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentToTextView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        document_file = request.FILES.get('document')
        
        if not document_file:
            return Response({'error': 'Нет документа'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_ext = os.path.splitext(document_file.name)[1].lower()
        if file_ext not in ['.pdf', '.docx']:
            return Response({'error': 'Поддерживаются только PDF и DOCX файлы'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        doc_model = DocumentFile(file=document_file)
        doc_model.save()
        
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, doc_model.file.name)
            
            text = extract_text_tables(file_path)
            
            doc_model.processed_text = text
            doc_model.save()
            
            grpc_response = send_to_grpc_server(text)
            
            return Response({
                'text': text,
                'grpc_response': grpc_response
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)