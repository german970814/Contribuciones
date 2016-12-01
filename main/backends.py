# Django Imports
from django.contrib.auth import get_user_model


class EmailAuthenticationBackend(object):
    """Backend de autentificación por email para usuarios."""

    def __init__(self):
        self.user_model = get_user_model()

    def authenticate(self, email=None, password=None):
        """Funcion encargada de autentificacion."""
        try:
            user = self.user_model.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
