# Django imports
from django.conf.urls import url

# Locale impors
from .views import (
    login_view, logout_view, home_view, SobreCreate
)
from .api import get_persona_api

urlpatterns = [
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^home/$', home_view, name='home'),
    url(r'^sobres/crear/$', SobreCreate.as_view(), name='crear_sobre'),
    # API
    url(r'^api/v1\.1/persona/(?P<id_persona>\d+)/$', get_persona_api, name='api>get_persona'),
]
