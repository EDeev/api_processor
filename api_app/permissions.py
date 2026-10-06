import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission


class ApiTokenPermission(BasePermission):
    """Если задан API_TOKEN, запросы должны нести заголовок Authorization: Bearer <токен>"""

    message = "Нужен заголовок Authorization: Bearer <API_TOKEN>"

    def has_permission(self, request, view):
        if not settings.API_TOKEN:
            return True
        header = request.headers.get("Authorization", "")
        return hmac.compare_digest(header, f"Bearer {settings.API_TOKEN}")
