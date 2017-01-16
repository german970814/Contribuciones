# Django imports
from django.db.models import QuerySet

from .mixins import CustomQuerySet


class PersonaQuerySet(CustomQuerySet, QuerySet):
    """QuerySet para personas."""

    pass
