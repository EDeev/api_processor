# api_project/api_project/wsgi.py
"""
WSGI config for api_project project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')

application = get_wsgi_application()
