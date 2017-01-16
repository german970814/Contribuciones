# Django imports
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Locale imports
from . import constants

# Python imports
from functools import wraps
import json


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


def login_required_api(view_func):
    """Decorador para saber si un usuario está logeado o no en una API, retornando una respuesta JSON."""

    @csrf_exempt
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # if request.user.is_authenticated():
        data = view_func(request, *args, **kwargs)
        return HttpResponse(
            json.dumps(data), content_type=constants.CONTENT_TYPE
        )
        # return HttpResponse(
        #     json.dumps({constants.RESPONSE_CODE: constants.RESPONSE_DENIED, 'message': 'User not authenticated'}),
        #     content_type=constants.CONTENT_TYPE
        # )
    return wrapped_view
