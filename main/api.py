# Django imports
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

# Locale imports
from .models import Persona
from .constants import (
    RESPONSE_SUCCESS, RESPONSE_DENIED,
    RESPONSE_ERROR, RESPONSE_NOT_FOUND,
    CONTENT_TYPE, RESPONSE_CODE
)

# Python imports
import json


@login_required
def get_persona_api(request, id_persona):
    """Retorna los datos de una persona a partir de un id."""

    data = {RESPONSE_CODE: RESPONSE_SUCCESS}

    if request.method == 'GET':
        try:
            persona = Persona.objects.get(id=id_persona)
            data['persona'] = persona.to_json()
        except Persona.DoesNotExist:
            data[RESPONSE_CODE] = RESPONSE_NOT_FOUND
            data['message'] = _('No se encontró la persona buscada')

    else:
        data[RESPONSE_CODE] = RESPONSE_DENIED
        data['message'] = _('Peticion Incorrecta')


    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)
