# Django imports
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q

# Locale imports
from .decorators import login_required_api
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


@login_required_api
def get_personas_api(request):
    """Retorna las personas en formato JSON."""

    data = {RESPONSE_CODE: RESPONSE_SUCCESS}

    if request.method == 'GET':
        value = request.GET.get('q', None)

        if value is not None:
            queryset = (
                Q(nombre__icontains=value) | Q(primer_apellido__icontains=value) |
                Q(segundo_apellido__icontains=value) | Q(cedula__icontains=value)
            )

            data['personas'] = Persona.objects.filter(queryset).to_json(
                fields=['nombre', 'primer_apellido', 'cedula']
            )[0:10]
        else:
            data[RESPONSE_CODE] = RESPONSE_ERROR
    else:
        data[RESPONSE_CODE] = RESPONSE_DENIED

    return data
