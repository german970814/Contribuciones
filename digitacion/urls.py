# Django imports
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

# locale imports
# from . import main

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('main.urls', namespace='main')),
    url(r'^/$', RedirectView.as_view(url="/login/")),
]
