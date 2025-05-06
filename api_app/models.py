# api_project/api_app/models.py
from django.db import models
import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class AudioFile(models.Model):
    file = models.FileField(upload_to=get_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Audio {self.id} - {self.uploaded_at}"

class DocumentFile(models.Model):
    file = models.FileField(upload_to=get_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_text = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Document {self.id} - {self.uploaded_at}"
