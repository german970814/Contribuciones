# Django Imports
from django.contrib import admin

# Apps Imports
from .models import Persona, Sobre, Observacion, TipoIngreso

admin.site.register(Persona)
admin.site.register(Sobre)
admin.site.register(Observacion)
admin.site.register(TipoIngreso)
