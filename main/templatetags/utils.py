# Django imports
from django import template
from django.contrib.auth.models import Group

__author__ = 'german alzate'

register = template.Library()


@register.filter
def pertenece_grupo(usuario, grupos):
    """
    Indica si un usuario pertenece a alguno de los grupos especificados,
    separado por comas
    """

    _grupos = grupos.split(',')  # intenta crear las listas con los valores

    if usuario.is_superuser and usuario.is_staff:  # si es superusuario
        return True

    return usuario.groups.filter(name__in=_grupos).exists()
