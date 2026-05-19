from rest_framework import authentication
from django.contrib.auth.models import User
import hashlib


class SessionTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom auth that checks for a user_id in the session.
    Set by our login/signup views.
    """
    def authenticate(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            request.user_id = user_id
            request.is_admin = request.session.get('is_admin', False)
        else:
            request.user_id = None
            request.is_admin = False
        return None  # Don't block unauthenticated requests
