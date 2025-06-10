from rest_framework.authentication import TokenAuthentication
from rest_framework import HTTP_HEADER_ENCODING

class CookieTokenAuthentication(TokenAuthentication):
    """Token authentication using the 'auth_token' cookie."""

    def authenticate(self, request):
        token = request.COOKIES.get('auth_token')
        if not token:
            return None
        return self.authenticate_credentials(token)
