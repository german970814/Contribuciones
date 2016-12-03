# Django imports
from django.conf.urls import url

# Locale impors
from .views import (
    login_view, logout_view, home_view, SobreCreate, SobreUpdate,
    PersonaCreate, PersonaUpdate, TipoIngresoCreate, TipoIngresoUpdate,
    ObservacionCreate, ObservacionUpdate, SobreList, PersonaList,
    TipoIngresoList, ObservacionList, reporte_contribuciones
)
from .api import get_persona_api

urlpatterns = [
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^home/$', home_view, name='home'),
    url(r'^sobres/crear/$', SobreCreate.as_view(), name='crear_sobre'),
    url(r'^sobres/editar/(?P<pk>\d+)/$', SobreUpdate.as_view(), name='editar_sobre'),
    url(r'^sobres/lista/$', SobreList.as_view(), name='listar_sobres'),
    url(r'^personas/crear/$', PersonaCreate.as_view(), name='crear_persona'),
    url(r'^personas/editar/(?P<pk>\d+)/$', PersonaUpdate.as_view(), name='editar_persona'),
    url(r'^personas/lista/$', PersonaList.as_view(), name='listar_personas'),
    url(r'^tipo_ingreso/crear/$', TipoIngresoCreate.as_view(), name='crear_tipo_ingreso'),
    url(r'^tipo_ingreso/editar/(?P<pk>\d+)/$', TipoIngresoUpdate.as_view(), name='editar_tipo_ingreso'),
    url(r'^tipo_ingreso/lista/$', TipoIngresoList.as_view(), name='listar_tipo_ingresos'),
    url(r'^observacion/crear/$', ObservacionCreate.as_view(), name='crear_observacion'),
    url(r'^observacion/editar/(?P<pk>\d+)/$', ObservacionUpdate.as_view(), name='editar_observacion'),
    url(r'^observacion/lista/$', ObservacionList.as_view(), name='listar_observaciones'),
    url(r'^reportes/contribuciones/$', reporte_contribuciones, name='reporte_contribuciones'),
    # API
    url(r'^api/v1\.1/persona/(?P<id_persona>\d+)/$', get_persona_api, name='api>get_persona'),
]
