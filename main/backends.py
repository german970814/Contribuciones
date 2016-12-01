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
        except self.user_model.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(id=user_id)
        except self.user_model.DoesNotExist:
            return None
