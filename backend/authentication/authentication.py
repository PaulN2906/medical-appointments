from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class ExpiringTokenAuthentication(TokenAuthentication):
    """Token authentication that verifies token expiry."""

    keyword = "Bearer"

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        expiry = getattr(settings, "TOKEN_EXPIRATION_TIME", timedelta(hours=1))
        if timezone.now() - token.created > expiry:
            token.delete()
            raise exceptions.AuthenticationFailed("Token has expired.")

        return (token.user, token)
