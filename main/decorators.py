# Django imports
from django.contrib.auth.decorators import user_passes_test


def group_required(grupos):
    """Chequea que el usuario pertenezca a alguno de los grupos ingresados."""

    if grupos:
        def decorator(user):
            return user.is_authenticated() and user.groups.filter(name__in=grupos).exists()
    else:
        decorator = lambda x: True

    return user_passes_test(decorator)
