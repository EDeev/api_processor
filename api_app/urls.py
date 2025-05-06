# api_project/api_app/urls.py
from django.urls import path
from .views import AudioToTextView, DocumentToTextView

urlpatterns = [
    path('audio-to-text/', AudioToTextView.as_view(), name='audio-to-text'),
    path('document-to-text/', DocumentToTextView.as_view(), name='document-to-text'),
]
