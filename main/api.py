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

    # crea la data con el codigo de respuesta predeterminado
    data = {RESPONSE_CODE: RESPONSE_SUCCESS}

    if request.method == 'GET':
        try:
            # intenta obtener la persona, con la url
            persona = Persona.objects.get(id=id_persona)
            # añade el json de la persona
            data['persona'] = persona.to_json()
        except Persona.DoesNotExist:
            # retorna la respuesta de error
            data[RESPONSE_CODE] = RESPONSE_NOT_FOUND
            # retorna un mensaje
            data['message'] = _('No se encontró la persona buscada')

    else:
        # retorna las respuestas adecuadas
        data[RESPONSE_CODE] = RESPONSE_DENIED
        data['message'] = _('Peticion Incorrecta')

    # retorna la respuesta en json
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)
