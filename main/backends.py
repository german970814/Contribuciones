# Django Imports
from django.contrib.auth import get_user_model


class EmailAuthenticationBackend(object):
    """Backend de autentificación por email para usuarios."""

    def __init__(self):
        # define un modelo de usuario
        self.user_model = get_user_model()

    def authenticate(self, email=None, password=None):
        """Funcion encargada de autentificacion."""
        try:
            # intenta obtener el usuario por el email
            user = self.user_model.objects.get(email=email)
            # checkea la contraseña
            if user.check_password(password):
                # retorna el usuario
                return user
        except self.user_model.DoesNotExist:
            # no retorna nada
            return None

    def get_user(self, user_id):
        try:
            # intenta obtener el usuario y lo retorna
            return self.user_model.objects.get(id=user_id)
        except self.user_model.DoesNotExist:
            # no retorna nada
            return None
