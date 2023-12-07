from typing import Optional, Any

from django.http import HttpRequest
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication


class GlobalJWTAuth(HttpBearer):
    """
    JWT authentication,
    thanks to https://github.com/vitalik/django-ninja/issues/305#issuecomment-1748822381 for the help
    """

    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        user_and_token = JWTAuthentication().authenticate(request)
        if user_and_token is not None:
            user = user_and_token[0]
            request.user = user
            request.claims = user_and_token[1]
            return user
        else:
            return None
