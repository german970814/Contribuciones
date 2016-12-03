# Django imports
from django.contrib.auth.decorators import user_passes_test


def group_required(*grupos):
    """Chequea que el usuario pertenezca a alguno de los grupos ingresados."""

    # si hay grupos
    if grupos:
        def decorator(user):
            # si es superusuario
            if user.is_staff and user.is_superuser:
                return True
            else:
                # si tiene los grupos
                return user.is_authenticated() and user.groups.filter(name__in=grupos).exists()
    else:
        decorator = lambda x: x.is_authenticated()

    # retorna la prueba
    return user_passes_test(decorator)
