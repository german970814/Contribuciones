"""
Procesadores de contextos para los templates con constantes
"""

from . import constants as constants_module


__author__ = 'German Alzate'


def constants(request):
    """Procesador de contexto de constantes."""

    data = {x: getattr(constants_module, x) for x in constants_module.__all__}

    return data
